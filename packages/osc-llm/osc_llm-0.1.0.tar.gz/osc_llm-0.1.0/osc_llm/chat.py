import re
import sys
import time
import warnings
from pathlib import Path
from typing import Iterator, List, Literal, Optional, Tuple

import lightning as L
import torch

# support running without installing as a package
wd = Path(__file__).parent.parent.resolve()
sys.path.append(str(wd))

from osc_llm.llm import LlamaConfig, Llama
from osc_llm.tokenizer import Tokenizer
from osc_llm.utils import check_valid_checkpoint_dir, get_default_supported_precision, lazy_load, quantization


@torch.no_grad()
def generate(
    model: Llama,
    idx: torch.Tensor,
    max_returned_tokens: int,
    max_seq_length: int,
    *,
    temperature: float = 1.0,
    top_k: Optional[int] = None,
    stop_tokens: Tuple[List[int], ...] = (),
):
    """Takes a conditioning sequence (prompt) as input and continues to generate as many tokens as possible.

    Args:
        model: The model to use.
        idx: Tensor of shape (T) with indices of the prompt sequence.
        max_returned_tokens: The maximum number of tokens to return (given plus generated).
        max_seq_length: The maximum sequence length allowed. Should be less or equal than the block size.
        temperature: Scales the predicted logits by 1 / temperature
        top_k: If specified, only sample among the tokens with the k highest probabilities
        stop_tokens: If specified, stop generating any more token once one of this list is generated.
    """
    T = idx.size(0)
    assert max_returned_tokens > T
    device = idx.device
    stop_tokens = [torch.tensor(tokens, device=device) for tokens in stop_tokens]
    input_pos = torch.arange(0, T, device=device)

    # buffer holds the tokens that haven't been yield yet
    buffer_length = max((len(tokens) for tokens in stop_tokens), default=1)
    buffer = torch.full((buffer_length,), -999, device=device)  # fill with non-existing token

    yield_i = -1
    # generate up to a fixed number of tokens
    for t in range(max_returned_tokens - T):
        # forward
        logits = model(idx.view(1, -1), input_pos)
        logits = logits[0, -1] / temperature

        # optionally crop the logits to only the top k options
        if top_k is not None:
            v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
            logits = torch.where(logits < v[[-1]], -float("Inf"), logits)

        probs = torch.nn.functional.softmax(logits, dim=-1)
        idx = torch.multinomial(probs, num_samples=1)

        # advance
        input_pos = input_pos[-1:] + 1


        # concatenate the new generation
        buffer[min(t, buffer_length - 1)] = idx

        # check the stop condition
        for tokens in stop_tokens:
            l = len(tokens)
            if torch.equal(buffer[-l:], tokens):
                # stop token hit, yield any leftovers that aren't part of it
                if buffer_length > l:  # avoid an empty yield
                    yield buffer[:-l]
                return
        # if the buffer is full
        if t - yield_i >= buffer_length:
            # we know this idx is not part of stop tokens, safe to yield
            yield buffer[0]
            # roll once to the left, as next generation will be put at the end
            buffer = torch.roll(buffer, -1, 0)
            yield_i += 1


def decode(fabric: L.Fabric, tokenizer: Tokenizer, token_stream: Iterator[torch.Tensor]) -> int:
    tokens_generated = 0
    if tokenizer.backend == "huggingface":
        for token in token_stream:
            fabric.print(tokenizer.decode(token), end="", flush=True)
            tokens_generated += 1
    elif tokenizer.backend == "sentencepiece":
        # sentencepiece does not support decoding token-by-token because it adds spaces based on the surrounding tokens
        # meaning that we need to decode everything each time
        so_far = torch.tensor([], dtype=torch.long, device=fabric.device)
        decoded_so_far = ""
        for token in token_stream:
            so_far = torch.cat((so_far, token.view(-1)))
            decoded_new = tokenizer.decode(so_far)
            fabric.print(decoded_new[len(decoded_so_far) :], end="", flush=True)
            decoded_so_far = decoded_new
            tokens_generated += 1
    else:
        raise NotImplementedError(tokenizer.backend)
    return tokens_generated


def main(checkpoint_dir: Path,
         accelerator: str = "cpu",
         devices: int = 1,
         top_k: int = 200,
         temperature: float = 0.8,
         quantize: Optional[Literal["bnb.nf4", "bnb.nf4-dq", "bnb.fp4", "bnb.fp4-dq", "bnb.int8", "gptq.int4"]] = None,
         precision: Optional[str] = None) -> None:
    """Starts a conversation with a tuned GPT model.

    Args:
        top_k: The number of top most probable tokens to consider in the sampling process.
        temperature: A value controlling the randomness of the sampling process. Higher values result in more random
            samples.
        checkpoint_dir: The checkpoint directory to load.
        quantize: Whether to quantize the model and using which method:
            - bnb.nf4, bnb.nf4-dq, bnb.fp4, bnb.fp4-dq: 4-bit quantization from bitsandbytes
            - bnb.int8: 8-bit quantization from bitsandbytes
            - gptq.int4: 4-bit quantization from GPTQ
            for more details, see https://github.com/Lightning-AI/lit-gpt/blob/main/tutorials/quantize.md
        precision: Indicates the Fabric precision setting to use.
    """
    precision = precision or get_default_supported_precision(training=False)

    check_valid_checkpoint_dir(checkpoint_dir)

    with open(checkpoint_dir / "llm_config.json") as fp:
        config = LlamaConfig()
    if accelerator == "cpu":
        fabric = L.Fabric(precision=precision, accelerator=accelerator)
    else:
        fabric = L.Fabric(precision=precision, accelerator=accelerator, devices=devices)

    if quantize == "gptq.int4":
        model_file = "llm_gptq.4bit.pth"
        if not (checkpoint_dir / model_file).is_file():
            raise ValueError("Please run `python quantize/gptq.py` first")
    else:
        model_file = "llm.pth"
    checkpoint_path = checkpoint_dir / model_file
    fabric.print(f"Loading model {str(checkpoint_path)!r} with {config.__dict__}", file=sys.stderr)
    with fabric.init_module(empty_init=True), quantization(quantize):
        model = Llama(config)
    with lazy_load(checkpoint_path) as checkpoint:
        model.load_state_dict(checkpoint.get("model", checkpoint), strict=quantize is None)

    model.eval()
    model = fabric.setup_module(model)

    tokenizer = Tokenizer(checkpoint_dir)
    system_prompt, stop_tokens = prompt_config(checkpoint_dir, tokenizer)

    while True:
        try:
            prompt = input(">> Prompt: ")
        except KeyboardInterrupt:
            break
        if not prompt:
            break
        prompt = system_prompt.format(prompt=prompt)
        encoded_prompt = tokenizer.encode(prompt, device=fabric.device)
        max_returned_tokens = model.config.block_size
        
        with fabric.init_tensor():
            model.build_kv_caches(batch_size=1)
            
        y = generate(
            model,
            encoded_prompt,
            max_returned_tokens,
            max_seq_length=max_returned_tokens,
            temperature=temperature,
            top_k=top_k,
            stop_tokens=stop_tokens,
        )
        fabric.print(">> Reply: ", end="")
        try:
            t0 = time.perf_counter()
            tokens_generated = decode(fabric, tokenizer, y)
            t = time.perf_counter() - t0
            model.clear_kv_caches()
            fabric.print(
                f"\nTime for inference: {t:.02f} sec total, {tokens_generated / t:.02f} tokens/sec", file=sys.stderr
            )
        except KeyboardInterrupt:
            # support stopping generation
            pass
        fabric.print()


def prompt_config(checkpoint_dir: Path, tokenizer: Tokenizer) -> Tuple[str, Tuple[List[int], ...]]:
    
    b_inst, e_inst = "[INST]", "[/INST]"
    b_sys, e_sys = "<<SYS>>\n", "\n<</SYS>>\n\n"
    system_prompt = (
        f"{b_inst} {b_sys}You are a helpful assistant, 你是一个乐于助人的助手.{e_sys} {{prompt}} {e_inst} "
    )
    stop_tokens = ([tokenizer.eos_id],)
    return system_prompt, stop_tokens
