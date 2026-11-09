# Synthetic record-order example

The following is an illustrative, invented sequence, **not** a valid DBF900 file:

```text
line 1  01  wellbore A characteristics
line 2  02  oil completion A
line 3  06  casing A
line 4  07  perforation A
line 5  01  wellbore B characteristics
line 6  13  location B (before its first completion)
line 7  02  gas completion B
line 8  06  casing B
```

Expected behavior: lines 3–4 receive completion A identifiers, line 6 remains unassigned, and line 8 receives completion B identifiers. Real fixed-width test fixtures should be generated only after checking the original copybook positions.
