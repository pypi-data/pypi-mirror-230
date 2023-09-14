# RegioHelden Email template

`rh_email_tpl` is a django app used to render RegioHelden styled HTML emails. It provides also multiple Django
templatetags used as helpers for building HTML emails.

This project is meant to be used internally by RegioHelden organisation, as it has the company styles and logos.

## Installation

Simply run:
```
pip install rh_email_tpl
```

And add `rh_email_tpl` to your django `INSTALLED_APPS`. I.e.: in `settings.py` add:
```
INSTALLED_APPS = [
  ...
  "rh_email_tpl",
  ...
]
```

## Making a new release

[bumpversion](https://github.com/peritus/bumpversion) is used to manage releases.

Add your changes to the [CHANGELOG](./CHANGELOG.md) and run `bumpversion <major|minor|patch>`, then push your change.
That is enough for the new release, once the MR was merged the new release will be published.
