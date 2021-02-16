bulma-popover
=============

This extension is based on the [bulma-tooltip] extension. This extension
allows for more complex content to be placed in the pop up. It is styled like
Bulma's builtin box element.

[bulma-tooltip]: https://github.com/Wikiki/bulma-tooltip


Classes
-------

- `popover` popover wrapper
- `popover-trigger` display popover when this element is focused
- `popover-content` the content of the popover


Positions
---------

Modifiers for selecting position:

- `.is-popover-top`
- `.is-popover-right`
- `.is-popover-bottom`
- `.is-popover-left`

Top is the default.


Active
------

To hold the popover open use the `.is-popover-active` modifier.


Example
-------

```html
<div class="popover is-popover-bottom">
  <button class="button is-primary popover-trigger">Table Popover</button>
  <div class="popover-content">
    <table class="table">
      <thead>
        <tr><th>Fruit</th><th>Color</th></tr>
      </thead>
      <tbody>
        <tr><td>Apple</td><td>Red</td></tr>
        <tr><td>Banana</td><td>Yellow</td></tr>
        <tr><td>Cucumber</td><td>Green</td></tr>
      </tbody>
    </table>
  </div>
</div>
```


Variables
---------

Name | Default Value
------------ | -------------
`$popover-max-width` | `24rem`
`$popover-color` | `$text`
`$popover-background-color` | `$white`
`$popover-radius` | `$radius` (4px)
