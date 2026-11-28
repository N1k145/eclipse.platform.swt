# SWT Test Font

`swt-test-font.ttf` is a minimal TrueType font used by
`Test_GtkDevice.test_loadFont` (on GTK only, see the TODO in
`Test_org_eclipse_swt_widgets_Display`). It was written for these
tests and is licensed under the EPL-2.0, like the generator next to it.

- Family "SWT Test Font", style Regular. The family name must not match an
  installed font, otherwise the test cannot tell whether `Display.loadFont`
  made the font available.
- Every printable ASCII character (U+0021..U+007E) is drawn as the same box,
  600 units wide. Space is an empty glyph.

## Regenerating the file

The font is written byte by byte by `generate-swt-test-font.py`, which only
needs Python 3 and its standard library (no font tools):

```bash
python3 generate-swt-test-font.py swt-test-font.ttf
```

The output is deterministic, so a regenerated file is identical to the
committed one unless the script changed. To check the result:

```bash
fc-scan --format='%{family} %{style} %{charset}\n' swt-test-font.ttf
# SWT Test Font Regular 20-7e
```
