# SwiftPage

### What is SwiftPage?

SwiftPage is a series of Python scripts that let you generate good-looking websites in minutes with no web development experience nor design intuition.  Generated SwiftPages are aesthetically-pleasing, incredibly easy to set up and edit, and mobile-friendly.

### What can I use SwiftPage for?

Need a quick and dirty webpage that doesn't look like crap?  SwiftPage will help you transform your one-off webpages from this:



To this:



SwiftPage will let you easily generate a well-designed, aesthetically pleasing webpage without knowing modern web development techniques or good design precedents.  It's quick and dirty webpages made easy and beautiful!

### What makes SwiftPage unique?

Many tools already exist for creating websites without needing to know any coding language or technical procedure.  Many of these tools, however, still require users to learn a new user interface or spend lots of extra time trying to make something aesthetically pleasing.

SwiftPage makes all of these issues pretty much trivial – SwiftPage lets you create content-rich webpages in *minutes* that look great *by default*.

### What are some SwiftPage examples?

My Website - http://www.magmhj.com

MIT Animation Groups Website - http://mitag.mit.edu

### How do I set up SwiftPage and what are its dependencies?

SwiftPage relies on one external Python package (at the moment), which can be installed using the following terminal command(s):

```
pip install Pillow
```

Setting up SwiftPage after installing these packages is very easy.  Simply download or clone this repository, and run `python create_page.py` to ensure that everything is working properly.

```
git clone [repository address of your choice]
cd swiftpage/
python create_page.py
```

### How do I use SwiftPage?

SwiftPage provides two scripts, `create_page.py` and `server.py` that you can run to generate a new HTML5 website in the `site/` directory.

The file `create_page.py` is where you define the content of your SwiftPage.  In the `Page` constructor, you specify the Components that will be rendered on the page, which is explained in further detail in the section below.

Running `python create_page.py` will look at the specified page, print warnings about potentially problematic design choices, and save a new HTML5 SwiftPage inside the `site/` directory *once*.

Running `python server.py`, on the other hand, will start a server that will detect when `create_page.py` has been changed, automatically regenerate the SwiftPage inside the `site/` directory, and refresh `dev.html` in your default web browser.  Therefore, with `server.py` running, you can edit `create_page.py` like an HTML file and see your changes automatically update in your web browser.

SwiftPage works by generating code that fits to the preexisting contents of the `site/` directory.  The idea is that you can drag any relevant images and files into the `site/` directory, then run `create_page.py` or `server.py` to automatically generate code that points to everything correctly so you don't have to worry about file paths and heirarchies!

**TL/DR:** `python create_page.py` generates your page *once*, `python server.py` generates your page whenever `create_page.py` changes.

### How can I customize my SwiftPages?

To customize your SwiftPage, change the rendered `Page` object in `create_page.py`.  `Page` objects can be created with a specified list of Components, like Rows, NavBars, and Sections.  Each of these Components has certain parameters which affect its appearance and behavior as follows:

#### Rows

Rows have lots of different capabilities, but they are the smallest singular units of information that SwiftPage parses and renders.  When constructing a new Row, its **first parameter** is a string that defines the Row's **type**, which determines what additional information it requires.  Its **second parameter** is a dictionary of **relevant metadata** about the Row that is specific for the Row's type.

Here is a list of currently-supported standalone Row types and the parameters they adhere to:



##### Type: Logo - "logo"

Metadata parameters:

- "filename": String, optional, name of logo image file within `images` directory
- "height": Integer, optional, changes the height of the logo image if "filename" is defined
- "text": String, optional, logo text, can be rendered when "filename" is defined or undefined
- "text-color": String hex code, optional, changes color of text when "text" is defined
- "rounded": String "true" or "false", optional, defines whether or not text is surrounded by rounded background
- "rounded-color": String hex code, optional, changes color of rounded background if "rounded" is "true"
- "rounded-border-color": String hex code, optional, changes color of rounded background border
- "background-colors": list of String hex codes, optional, changes background color to gradient between the first and last provided colors
- "background-filename": String, optional, name of background image file within `images` directory
- "snippet": String, optional, HTML snippet of code that is rendered if "filename" and "text" are both not defined

Example construction:

```
Row("logo", {
    "text": "My Projects SwiftPage",
    "rounded": "true",
    "background-colors": ["#f06d55", "#1a32d5"],
})
```

Appearance:

![row_header](readme_resources/row_header.png)



##### Type: Footer - "footer"

Metadata parameters:

- "snippet": String, optional, HTML snippet of code
- "text": String, optional, text that is rendered when "snippet" is not defined
- "text-color": String hex code, optional, changes color of text
- "background-colors": list of String hex codes, optional, changes background color to gradient between the first and last provided colors

Example construction:

```
Row("footer", {
    "text": "All Rights Reserved.",
    "text-color": "#242424",
})
```

Appearance:

![row_header](readme_resources/row_footer.png)



All other Row types are not intended for standalone use – they are created and managed by Section objects, which are explained further in the section below.

#### Sections



#### NavBars