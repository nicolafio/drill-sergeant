# Drill Sergeant

## Project aims

Drill Sergeant helps on the planning and execution of
daily activities by presenting common tools in an unified
environment. Drill Sergeant also helps visualize progress
[...]. You can use Drill Sergeant to establish a routine
and see how well you can stick to it. Drill Sergeant
helps your motivation by reporting your progress though
charts. [...expand on other gamification ideas, like virtual currency, levelling, and sandbox-like games]

Drill Sergeant is a distributed system from the start.
It can do two-way syncrhonization with other instances
in Drill Sergeant so that you can keep your progress in
multiple devices and/or in a server.

- web service support.
- macOS support.
- importing/exporting events in common formats (iCalendar, JSON)
- iPad support.
- iPhone support.

## Setup

_These instructions are for macOS_

* Install [VSCodium](https://vscodium.com/) or [VSCode](https://code.visualstudio.com/).
    * If using VSCodium, switch the extension registry from Open VSX to Microsoft's VS Code as noted [below](#switching-extension-registry-to-vscode).

#### Switching extension registry to VScode

Replace content of `~/Library/Application Support/VSCodium/product.json`
with the following:

```json
{
    "extensionsGallery": {
        "serviceUrl": "https://marketplace.visualstudio.com/_apis/public/gallery",
        "itemUrl": "https://marketplace.visualstudio.com/items",
        "cacheUrl": "https://vscode.blob.core.windows.net/gallery/index",
        "controlUrl": ""
    }
}
```

<small> Reference: VSCodium contributors, Nov 2023, [_How to use a different extension gallery_](https://github.com/VSCodium/vscodium/blob/f3a6b95/docs/index.md#how-to-use-a-different-extension-gallery), GitHub</small>
