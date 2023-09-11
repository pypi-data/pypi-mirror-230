# PyTint

python package to colorize envy icons, themes, etc.

## how does it work?

the pytint module operates on a single svg file, or a directory of svg files. it
takes an input blueprint, and converts the basic colors into the selected
scheme.

**the main blueprint scheme should consist of a combination of 5 colors:**

main colors:

-   <span style=" background-color: #00FF00; color: #000;">\#00FF00</span>:
    default color
-   <span style=" background-color: #0000FF; color: #FFF;">\#0000FF</span>:
    accent color

scheme colors:

-   <span style=" background-color: #FF0000; color: #000;">\#FF0000</span>:
    background color
-   <span style=" background-color: #FFFFFF; color: #000;">\#FFFFFF</span>:
    background accent color
-   <span style=" background-color: #000000; color: #FFF;">\#000000</span>:
    difference color

**those colors are then converted in the following way:**

-   <span style=" background-color: #00FF00; color: #000;">\#00FF00</span>
    &#8594; default
-   <span style=" background-color: #0000FF; color: #FFF;">\#0000FF</span>
    &#8594; accent
-   <span style=" background-color: #FF0000; color: #000;">\#FF0000</span>
    &#8594; variant
-   <span style=" background-color: #FFFFFF; color: #000;">\#FFFFFF</span>
    &#8594; alt
-   <span style=" background-color: #000000; color: #FFF;">\#000000</span>
    &#8594; difference

**examples:**

purple color, light scheme

-   default:
    <span style=" background-color: #00FF00; color: #000;">\#00FF00</span>
    &#8594;
    <span style=" background-color: #9141AC; color: #FFF;">\#9141AC</span>
-   accent:
    <span style=" background-color: #0000FF; color: #FFF;">\#0000FF</span>
    &#8594;
    <span style=" background-color: #DC8ADD; color: #000;">\#DC8ADD</span>
-   variant:
    <span style=" background-color: #FF0000; color: #000;">\#FF0000</span>
    &#8594;
    <span style=" background-color: #3D3846; color: #FFF;">\#3D3846</span>
-   alt: <span style=" background-color: #FFFFFF; color: #000;">\#FFFFFF</span>
    &#8594;
    <span style=" background-color: #77767b; color: #FFF;">\#77767b</span>
-   difference:
    <span style=" background-color: #000000; color: #FFF;">\#000000</span>
    &#8594;
    <span style=" background-color: #DEDDDA; color: #000;">\#DEDDDA</span>

yellow color, dark scheme

-   default:
    <span style=" background-color: #00FF00; color: #000;">\#00FF00</span>
    &#8594;
    <span style=" background-color: #F6D32D; color: #000;">\#F6D32D</span>
-   accent:
    <span style=" background-color: #0000FF; color: #FFF;">\#0000FF</span>
    &#8594;
    <span style=" background-color: #F9F06B; color: #000;">\#F9F06B</span>
-   variant:
    <span style=" background-color: #FF0000; color: #000;">\#FF0000</span>
    &#8594;
    <span style=" background-color: #DEDDDA; color: #000;">\#DEDDDA</span>
-   alt: <span style=" background-color: #FFFFFF; color: #000;">\#FFFFFF</span>
    &#8594;
    <span style=" background-color: #FEFEFE; color: #000;">\#FEFEFE</span>
-   difference:
    <span style=" background-color: #000000; color: #FFF;">\#000000</span>
    &#8594;
    <span style=" background-color: #3D3846; color: #FFF;">\#3D3846</span>

orange color, dark scheme, inverted

-   default:
    <span style=" background-color: #00FF00; color: #000;">\#00FF00</span>
    &#8594;
    <span style=" background-color: #FF7800; color: #000;">\#FF7800</span>
-   accent:
    <span style=" background-color: #0000FF; color: #FFF;">\#0000FF</span>
    &#8594;
    <span style=" background-color: #FFBE6F; color: #000;">\#FFBE6F</span>
-   variant:
    <span style=" background-color: #FF0000; color: #000;">\#FF0000</span>
    &#8594;
    <span style=" background-color: #3D3846; color: #FFF;">\#3D3846</span>
-   alt: <span style=" background-color: #FFFFFF; color: #000;">\#FFFFFF</span>
    &#8594;
    <span style=" background-color: #77767b; color: #FFF;">\#77767b</span>
-   difference:
    <span style=" background-color: #000000; color: #FFF;">\#000000</span>
    &#8594;
    <span style=" background-color: #DEDDDA; color: #000;">\#DEDDDA</span>

## usage

### pytint

colorize a single svg file

```py
from pytint.pytint import PyTint

# blueprint file
svg_in = "/home/user/blueprints/blueprint.svg"
# output file
svg_out = "/home/user/colorized/red.svg"

PyTint("red", "dark").tint_svg(svg_in, svg_out)

```

colorize all svgs in a directory

```py
svg_dir = "/home/user/blueprints"
out_dir = "/home/user/colorized"

# use inverted scheme (light theme uses dark colors)
PyTint("blue", "light", inverse_scheme=True).tint_batch(svg_dir, out_dir)
```

### colors

get default values list

```py
from pytint.colors import Colors

cols = Colors()
default_colors = cols.get_defaults()
print(f"default colors:\n{default_colors}")
```

get scheme variants list

```py
variants = cols.get_scheme_variants()
print(f"available variants:\n{variants}")
```

get supported colors list

```py
colors = cols.get_colors_list()
print(f"available colors:\n{colors}")
```

select scheme

```py
# normal
variant, alt, difference = cols.select_scheme("dark")
# inverted
variant, alt, difference = cols.select_scheme(variants[1], inverse=True)
```

select color

```py
default, accent = cols.select_color("blue")
print("blue: ", default, accent)
default, accent = cols.select_color(colors[0])
print(f"{colors[0]}: ", default, accent)
```
