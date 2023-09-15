# mactop

## Design Your Own Mactop

We use HTML + CSS style to setup the layout.

You can use `id` or `class` to select the element, like this:

```html
<Mactop>
  <layout>
    <Horizontal id="row-1">
      <SensorsPanel></SensorsPanel>
    </Horizontal>
  </layout>

  <style>
    #row-1 {
      color: red;
    }
  </style>
</Mactop>
```

Components do not support inline-css, but you can set attributes on components.

Common attributes that every components support:

- `id`;
- `class` or `classes`, separated by space;
- `refresh_interval`: set this will overwrite command line arguments
  `--refresh-interval` for that component.
