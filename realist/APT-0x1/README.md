# APT213 - There's a phish in the mailbox

**`Author:`** [hfz](https://hfz1337.github.io)

## Description

Snail Corp got phished (again), but this time it's not that kind of usual emails, it's much more. This seems like a targeted attack, an advanced persistent threat, and whoever is behind this surely got pissed off by their services.

The phishing email was so well crafted that it tricked their marketing employee into thinking that the document was highly confidential, and contained plans for infrastructure migration to provide better internet services–but we know far well that this isn't something to expect from Snail Corp, seriously, who would believe that?

Unfortunately, the employee–dying of curiosity–downloaded the attachment and detonated its malicious behavior, which resulted in the compromise of his machine. The employee's device was then used to move laterally inside the network and compromise other machines to achieve persistence while staying stealthy. This happened months ago and it's only recently that IoC's started to pop out.

The security team tried to isolate the compromised machines and extract the malware sample out of them, but unfortunately, the malware deleted itself before they had a chance to extract it and didn't leave any evidence. This brought them back to case zero, all they have is the phishing email and the attachment.

You are hired to track down the threat actors behind this attack and possibly provide a solution for the encrypted files. They provided you with the email's screenshot and the attached file.

This is a four (4) part mission, good luck.

DISCLAIMER: It is strongly adviced to use a VM if you're working on Windows. The author will not be held responsible for any damage caused as a result of a bad manipulation of the provided artifacts.
The archive is protected with the password: "iunderstandtherisk".

## Write-up (todo)
Check this [PR](https://github.com/Shellmates/BSides-Algiers-2k21-CTF-Quals/pull/11) for a general overview on the solution.


Flag: `shellmates{tr1ck_4l1_th3_t0Ols_h4cK_41l_tH3_th1Ngs_st0mP_0n_uR_f@ce!}`
