# apindex - Script that, given `tree -Js`, creates a static HTML directory listing

### Quick install
```sh
curl https://raw.githubusercontent.com/flashcarts/apindex/master/install.sh | bash
```

### What is this?

This is a program that generates `index.html` files in each directory on your server using the output of `tree -Js`. This is useful for static web servers that need support for file listing. One example of this is GitHub Pages.

It can also be used to reduce the server load for servers that serve static content, as the server does not need to generate the index each time it is accessed. Basically permanent cache.

The file icons are also embedded into the `index.html` file so there is no need for aditional HTTP requests.

### How do I use it?

0. Install apindex
    - Check Quick install or "How do I install it?" section on how to do so
1. Run `tree -Js > tree.json` from the root of your files
1. Run `apindex <path to tree.json>`
    - Optional: if your files are meant to be hosted on a different base URL than the generated HTML files, you can specify `-b <base URL>`
        - This does not assume you add a trailing slash. While it won't break the site, it won't look pretty
1. The HTML files will be written to `$PWD/site` directory
    - You can change this behaviour using `-o <path>`
    - The file directory and the site directory can be merged just by copy-pasting it all

### How do I install it?

```
git clone https://github.com/flashcarts/apindex
cd apindex
cmake . -DCMAKE_INSTALL_PREFIX=/usr/local
sudo make install
```

### How do I add/remove icons?
See `share/icons.xml` and the files under `share/img/*`.
