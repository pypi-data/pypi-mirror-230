## Summary

(Before creating an issue, please read https://gitlab.com/portmod/portmod/-/wikis/Reporting-Issues)

(Summarize the encountered bug concisely)

(Package-specific issues should be opened on the issue tracker for the package repository in question.
The repository a package comes from can be found in the transaction list at the end of the package name in the form ::repo when running in verbose mode, and will normally show up when using the search interface.
If in doubt, open the issue on the package repository first. Issues can be moved later if it is determined there is an underlying problem with portmod, or a related issue can be opened.
Do not open issues such as "installation of package X fails" on the main portmod issue tracker. Either report what in particular is wrong with portmod, or, if you don't know, open the issue on the package repository issue tracker.)

## Steps to Reproduce

(How can this issue be reproduced?)
(Which packages cause the issue? (try multiple before opening an issue that isn't package-specific))

## Current Behaviour

(Include a stack trace and output log if relevant.)
(You should enable the `--verbose` option, which may include more information, if the problem is unclear)
(Only provide CLI output that is relevant to the issue. E.g. if an issue occurs during package installation, it is usually not necessary to include full install logs for every package that installed before it.)

<details><summary>Output</summary>

```
<Output goes here>
```
</details>

## Expected Behaviour

(If the behaviour is unusual, but not fatal, what is the expected behaviour?)
(Omit if not relevant, such as if it fails completely and crashes portmod)

## Portmod and Prefix Information

<details><summary>prefix info</summary>

```
(include the output of `portmod <prefix> info` here)
```
</details>

(Also include any other relevant information such as if you're using a version from a branch, or have custom changes not available in the repository)

## Possible fixes

(If you can, link to the line of code which may be responsible for the problem)
(If you know of any changes which can be made to fix this, list them here)

/label ~bug
