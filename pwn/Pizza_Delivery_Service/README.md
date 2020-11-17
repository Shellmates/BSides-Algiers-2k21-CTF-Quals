# Challenge Name

**`Author:`** [LaidMalik](https://github.com/malikDaCoda)

## Description

> Take a look at this pizza delivery service ! It's a little idea I was working on.  
> Hopefully there's nothing to be worried about :)

## Write-up

### Brief Summary

- orders can still be edited after being delivered (freed) => tcache poisoning
- orders can still be viewed after being delivered (freed) => get leaks
- if we get control over `current_user->name_size` => stack buffer overflow (in login func
tion)

### TODO

Flag: `shellmates{m4N1Pul4t1nG_piz7a_ChunK$!}`
