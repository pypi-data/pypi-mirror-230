import base64
import io
import torch
from typing import Dict
from torch import autocast
from diffusers import StableDiffusionPipeline
from kservehelper import KServeModel
from kservehelper.types import Input


class StableDiffusion:

    def __init__(self):
        self.device = None
        self.text2img_pipe = None

    def load(self):
        model_path = "/mnt/models/stable-diffusion/v1_4"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.text2img_pipe = StableDiffusionPipeline.from_pretrained(
            model_path).to(self.device)

    def predict(
            self,
            prompt: str = Input(
                description="Input prompt",
                default="a dog playing on the street"
            ),
            guidance_scale: float = Input(
                description="Guidance scale",
                default=7.5
            ),
            height: int = Input(
                description="Image height",
                default=512
            ),
            width: int = Input(
                description="Image width",
                default=512
            ),
            num_inference_steps: int = Input(
                description="The number of inference steps",
                default=50
            ),
            seed: int = Input(
                description="Random seed",
                default=12345
            ),
            safety_check: bool = Input(
                description="Do safety check",
                default=False
            )
    ) -> Dict:
        if not safety_check:
            self.text2img_pipe.safety_checker = lambda images, **kwargs: (images, False)
        generator = torch.Generator(self.device)
        generator.manual_seed(seed)

        with autocast(self.device):
            image = self.text2img_pipe(
                prompt=prompt,
                guidance_scale=guidance_scale,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                generator=generator
            ).images[0]

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        im_b64 = base64.b64encode(buffer.getvalue())
        return {"image": im_b64}


if __name__ == "__main__":
    KServeModel.serve("stable-diffusion", StableDiffusion)
