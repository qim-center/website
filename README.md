# Qim website

This site is built with [Hugo](https://gohugo.io/).

**Any changes pushed to the `main` branch are deployed live within ~2 minutes.**

## Local development

1. Clone the repo
2. Run `hugo serve`
3. Go to http://localhost:1313/

---

## How to update cards in the About page

Team member cards are defined as individual YAML files in `data/about/members/`.

To add or edit a team member:

1. Create or edit a file in `data/about/members/` (e.g. `john-doe.yaml`)
2. Follow this structure:

```yaml
name: "John Doe"
group: "Staff"                     # One of: QIM Lead, Staff, Development Team, Working Group
role:                              # string or list of strings
  - "Researcher"
affiliation: "DTU Compute"
image: "/images/about/john-doe.jpg"
bio: "Short biography text."
links:
  - label: "Email"
    icon: "fa-regular fa-envelope"
    href: "mailto:johnd@dtu.dk"
  - label: "LinkedIn"
    icon: "fa-brands fa-linkedin"
    href: "https://linkedin.com/in/john-doe"
weight: 30                         # lower = higher position in the list
```

3. Place the headshot image in `assets/images/about/` (referenced as `/images/about/...` in the YAML)
4. Commit and push to `main`

---

## How to add new showcases

Each showcase requires **two files**: a content page and a data entry.

### 1. Create a content file

Create a file in `content/showcases/` (e.g. `my-showcase.md`):

```toml
+++
author = "QIM"
title = "My Showcase"
description = "Brief description of the showcase"
tags = ["Tag1", "Tag2"]
image = "images/showcases/my-showcase.png"
repo = "https://github.com/qim-center/my-showcase"
branch = "main"
raw_base = "https://raw.githubusercontent.com/qim-center/my-showcase/main/"
report = "https://raw.githubusercontent.com/qim-center/my-showcase/main/report.md"
+++

<!-- Content fetched from remote repository at build time -->
```

The `report` URL must point to a markdown file in the remote repository — this is rendered as the showcase detail page content.

### 2. Add a data entry

Add the corresponding entry to `data/showcases.yaml`:

```yaml
showcases:
  - id: my-showcase                       # must match the content filename (without .md)
    title: "My Showcase"
    description: "Brief description of the showcase"
    tags: ["Tag1", "Tag2"]
    repo: https://github.com/qim-center/my-showcase
    branch: main
    raw_base: https://raw.githubusercontent.com/qim-center/my-showcase/main/
    report: https://raw.githubusercontent.com/qim-center/my-showcase/main/report.md
    image: images/showcases/my-showcase.png
```

### 3. Add the image

Place the image in `assets/images/showcases/`.

---

## How to add Software tools

Create a file in `content/tools/` (e.g. `my-tool.md`):

```toml
+++
title = "My Tool"
description = "Short description of what the tool does."
authors = ["Author Name"]
tags = ["Tag1", "Tag2"]
image = "images/tools/my-tool.png"
source_url = "https://github.com/qim-center/my-tool"
+++

Brief description of the tool. You can use markdown and the `{{< fig >}}` shortcode for images.

{{< fig src="/images/tools/my-tool/figure1.png" caption="Optional figure caption." >}}
```

- Body images go in `assets/images/tools/my-tool/` and are referenced as `/images/tools/my-tool/...`
- The `image` frontmatter field is the card thumbnail, placed in `assets/images/tools/`
- The GitHub link is automatically shown based on `source_url`

---

## How to edit/add Research support pages

Support pages live in `content/support/`. The section index is `content/support/_index.md`.

To add a new support page, create a file in `content/support/` (e.g. `my-service.md`):

```toml
+++
title = "My Service"
description = "Brief description of the service."
icon = "fa-cube"                    # FontAwesome icon class
image = "images/support/support.jpg"
+++

Markdown content describing the service. Use the `{{< fig >}}` shortcode for images.
```

Available FontAwesome icons can be found at https://fontawesome.com/icons.

To edit an existing page, simply edit the corresponding `.md` file in `content/support/`.

---

## How to add/modify events

Event files live in `content/events/`. The section index is `content/events/_index.md`.

### Add a new event

Create a file in `content/events/` (e.g. `my-event.md`):

```toml
+++
title = "My Event"
description = "Short description of the event."
location = "Venue name, City, Country"
date = "2026-06-15"                 # YYYY-MM-DD format
cta_link = "https://example.com/register"   # optional — only shown for upcoming events
cta_text = "Register Now"                   # optional, defaults to "Register"
image = "images/events/my-event.png"
+++

Markdown body describing the event program or details.
```

- Events with a date in the future appear under **Upcoming Events**
- Events with a past date appear under **Past Events**
- If a `cta_link` is set, the button only shows for upcoming events
- Event images go in `assets/images/events/`

### Modify an existing event

Edit the corresponding `.md` file in `content/events/`. Change the `date` field to move it between upcoming and past sections.
