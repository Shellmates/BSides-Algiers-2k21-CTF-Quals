# Homer The Simp - 0x3

**`Author:`** [hfz](https://hfz1337.github.io)

## Description


## Write-up (pseudo writeup, might give more explanations later)

From Homer's `note.txt`, we understand that he'll be training a model with PyTorch then handing that over to Marge. If you take a look at PyTorch's documentation [here](https://pytorch.org/docs/stable/generated/torch.load.html), you'll notice a **WARNING** stating that you should not load models coming from untrusted sources, and this is because `torch`'s `load` function uses `pickle` under the hood, which can lead to arbitrary code execution.
To exploit `marge`, we have to craft a malicious archive that will be fed into `torch.load` (kinda, I simulated how `torch` proceeds in a [short script](../homer-the-simp-0x2/marge/root/model_loader.py) instead of installing a huge module inside a container just for that matter).
Create a folder called `archive` and put `data.pkl` inside it (`data.pkl` is the malicious pickle file), after that:
```bash
$ zip -r payload.pth archive
```
The file extension `pth` is specific to PyTorch models and is **important** in this challenge, as `marge` will only download model files.
Drop `payload.pth` insides `Homer`'s **exam** folder, wait up to a minute for the job to run, and you should get command execution.

Flag: `shellmates{3v3n_pYt0rcH_d0cUm3nt@t10n_w4rnS_y0u_4b0ut_1T}`
