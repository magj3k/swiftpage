# SwiftPage

### What is SwiftPage?

SwiftPage is a series of Python scripts that let you generate good-looking websites in minutes with no web development experience nor design intuition.  Generated SwiftPages are aesthetically-pleasing, incredibly easy to set up and edit, and mobile-friendly.

### What can I use SwiftPage for?

Need a quick and dirty webpage that doesnt look like crap?  SwiftPage will help you transform your one-off webpages from this:



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

Running `python server.py`, on the other hand, will start a server that will detect when `create_page.py` has been changed and automatically regenerate the SwiftPage inside the `site/` directory.  Therefore, with `server.py` running, you can edit `create_page.py` like an HTML file and refresh your browser to see changes.

**TL/DR:** `python create_page.py` generates your page *once*, `python server.py` generates your page whenever `create_page.py` changes.

### How can I customize my SwiftPages?

