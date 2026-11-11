# Formatted hyperlink paste guidance

Easy Hyperlink writes both HTML (the named anchor) and plain text (the original URL) to the clipboard when supported by the browser. The destination chooses which clipboard format it accepts. The tool does not change the destination URL or file permissions.

The page lists editors that support named hyperlinks. This is documentation-based guidance, not a tested browser/app compatibility matrix. Rich-text import, app versions, compose modes, and paste options can affect whether the label survives.

- [Microsoft Teams links](https://support.microsoft.com/en-us/teams/chat/send-a-file-picture-or-link-in-microsoft-teams): the formatted chat/channel composer supports display text and a URL via Format → Insert link. Clipboard import can vary.
- [Zoom Chat message formatting](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0066130): the rich-text composer supports a link on selected text. This does not establish identical behavior for every in-meeting chat client. [Zoom release notes](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0064537) also document administrator controls that can disable hyperlinks.
- [Gmail formatting](https://support.google.com/mail/answer/8260?co=GENIE.Platform%3DDesktop): use the message body with plain text mode disabled.
- [Outlook formatting](https://support.microsoft.com/en-us/outlook/format-email-messages-in-outlook-for-mac): use an HTML message body and preserve formatting when pasting.
- [Word paste options](https://support.microsoft.com/en-us/word/control-the-formatting-when-you-paste-text): Keep Source Formatting preserves source formatting.
- [Google Docs links](https://support.google.com/docs/answer/45893?hl=en) and [copy/paste](https://support.google.com/docs/answer/161768?hl=en): document text supports editable link text and destinations.
- [Notion links](https://www.notion.com/help/create-links-and-backlinks): page text supports external links. Different fields may handle pasted content differently.

Use normal paste. Plain-text paste or a plain-text destination loses the HTML representation. If formatted paste is unavailable, use the destination's Insert link command with the original URL. Link styling is controlled in the destination editor.

The example uses the public [Python functions guide](https://docs.python.org/3/tutorial/controlflow.html#defining-functions). It is an illustrative work email, not a claim about a real customer or a measured time saving.
