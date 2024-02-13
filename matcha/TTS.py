import random
import time
from pathlib import Path
from pydub import AudioSegment
import numpy as np
import torch
from matcha.hifigan.config import v1
from matcha.hifigan.denoiser import Denoiser
from matcha.hifigan.env import AttrDict
from matcha.hifigan.models import Generator as HiFiGAN
from matcha.models.matcha_tts import MatchaTTS
from matcha.text import sequence_to_text, text_to_sequence
from matcha.text.numberworks_ky import numberreader
from matcha.utils.utils import intersperse
import json
def process_text(i: int, text: str, device: torch.device):
    print(f"[{i}] - Input text: {text}")
    x = torch.tensor(
        intersperse(text_to_sequence(text, ["kygryz_cleaners2"]), 0),
        dtype=torch.long,
        device=device,
    )[None]
    x_lengths = torch.tensor([x.shape[-1]], dtype=torch.long, device=device)
    x_phones = sequence_to_text(x.squeeze(0).tolist())
    print(f"[{i}] - Phonetised text: {x_phones[1::2]}")

    return {"x_orig": text, "x": x, "x_lengths": x_lengths, "x_phones": x_phones}


def load_hifigan(checkpoint_path, device):
    h = AttrDict(v1)
    hifigan = HiFiGAN(h).to(device)
    hifigan.load_state_dict(torch.load(checkpoint_path, map_location=device)["generator"])
    _ = hifigan.eval()
    hifigan.remove_weight_norm()
    return hifigan


def load_vocoder(vocoder_name, checkpoint_path, device):
    print(f"[!] Loading {vocoder_name}!")
    vocoder_name = 'hifigan_T2_v1'
    if vocoder_name in ("hifigan_T2_v1", "hifigan_univ_v1"):
        vocoder = load_hifigan(checkpoint_path, device)
    else:
        raise NotImplementedError(
            f"Vocoder {vocoder_name} not implemented! define a load_<<vocoder_name>> method for it"
        )

    denoiser = Denoiser(vocoder, mode="zeros")
    print(f"[+] {vocoder_name} loaded!")
    return vocoder, denoiser



def load_matcha(model_name, checkpoint_path, device):
    print(f"[!] Loading {model_name}!")
    model = MatchaTTS.load_from_checkpoint(checkpoint_path, map_location=device)
    _ = model.eval()

    print(f"[+] {model_name} loaded!")
    return model


def to_waveform(mel, vocoder, denoiser=None):
    audio = vocoder(mel).clamp(-1, 1)
    if denoiser is not None:
        audio = denoiser(audio.squeeze(), strength=0.00025).cpu().squeeze()

    return audio.cpu().squeeze()


def save_to_folder(filename: str, output: dict, folder: str):
    folder = Path(folder)
    folder.mkdir(exist_ok=True, parents=True)
    waveform = output["waveform"]
    waveform_int = np.int16(waveform * 32767.0)
    audio_segment = AudioSegment(
        waveform_int.tobytes(),
        frame_rate=22050,
        sample_width=2,
        channels=1
    )
    audio_segment.export(folder / f"{filename}.mp3", format="mp3")
    return folder.resolve() / f"{filename}.mp3"


def unbatched_synthesis(args, device, model, vocoder, denoiser, texts):
    all_outputs = []
    for i, text in enumerate(texts):
        i = i + 1
        text = text.strip()
        text_processed = process_text(i, text, device)
        output = model.synthesise(
            text_processed["x"],
            text_processed["x_lengths"],
            n_timesteps=args['steps'],
            temperature=args['temperature'],
            spks=None,
            length_scale=args['speaking_rate'],
        )
        output["waveform"] = to_waveform(output["mel"], vocoder, denoiser)
        all_outputs.append(output["waveform"])
    merged_waveform = np.concatenate(all_outputs)
    file_name = f"{int(time.time())}audio{random.randint(1, 1000000)}"
    return save_to_folder(file_name, {"waveform": merged_waveform}, args['output_folder'])


class TTS():
    def __init__(self, speaker_id, device=0):
        with open('./matcha/config.json', 'r') as f:
            self.config = json.load(f)
        self.args = self.config.get('args')
        self.device = self.args['device']+str(device)
        self.paths = {"matcha": self.config.get('models').get(str(speaker_id)), "vocoder": self.args['vocoder_path']}
        self.model = load_matcha(self.args['model'], self.paths["matcha"], self.device)
        self.vocoder, self.denoiser = load_vocoder(self.args['vocoder'], self.paths["vocoder"], self.device)

    @torch.inference_mode()
    def generate_audio(self, text):
        text = numberreader(text)
        return unbatched_synthesis(self.args, self.device, self.model, self.vocoder, self.denoiser, [text])
