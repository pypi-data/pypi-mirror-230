"""
Ugly and terribly simple viewer for newpyter notebook.
It can show ipynb too, as well as traverse the github (given that API token is provided).

See /demo/viewer for instructions how to start this server

Main TODOs
- better app styling
- reduce code ugliness by using templates

"""
import html
import tempfile
from pathlib import Path
from typing import Tuple, Optional

import sh
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from nbconvert import HTMLExporter

from newpyter.ContentsManager import NewpyterContentsManager

style = """
<style>
body {
    min-width: 800px;
    max-width: 1200px;
    margin: 50px auto;
}
.collapsed-input {
    max-height: 32px;
    opacity: 0.5;
}
.jp-RenderedImage img.full-width-image, img.full-width-image {
    max-width: initial;
}
</style>
"""


class NewpyRouter:
    def __init__(self, github_token: str, start_repo: str, newpyter_toml_path: Path, web_basedir='/'):
        self.github_token = github_token
        self.start_repo = start_repo
        self.newpyter_toml_path = newpyter_toml_path
        self.web_basedir = web_basedir

        self.app = FastAPI()
        self.router = self.app
        self.subapp = FastAPI()
        self.app.mount(web_basedir, self.subapp)

        @self.subapp.get('/', response_class=HTMLResponse)
        def frontpage() -> str:
            return self.frontpage()

        @self.subapp.get('/source', response_class=HTMLResponse)
        def read_source(source: str) -> str:
            return self.read_source(source=source)

        @self.subapp.get('/github', response_class=HTMLResponse)
        def read_github(github_permalink: str) -> str:
            return self.read_github(github_permalink=github_permalink)

        @self.subapp.get('/github_dir', response_class=HTMLResponse)
        def list_github(repo: str = '', path_in_repo: str = ''):
            return self.list_github(repo=repo, path_in_repo=path_in_repo)

    def frontpage(self):
        return style + render_form(app=self.router, default_repo=self.start_repo)

    def read_source(self, source: str) -> str:
        return render_form(source=source, app=self.router) + convert_newpy_text_to_html(source) + style

    def read_github(self, github_permalink: str) -> str:
        if "github" in github_permalink:
            html, newpyter_source = download_and_convert(github_permalink, secret=self.github_token,
                                                         newpyter_toml=self.newpyter_toml_path)
            contents = style + render_form(url=github_permalink, source=newpyter_source, app=self.router,
                                           collapse_code=True) + html
            return contents
        else:
            return f"Did not recognize link: {render_form(url=github_permalink, app=self.router) + github_permalink}"

    def list_github(self, repo: str = '', path_in_repo: str = '') -> str:
        result = download_and_render_link_list(
            github_token=self.github_token,
            repo=self.start_repo if repo == '' else repo,
            path_in_repo=path_in_repo,
            app=self.router,
        ) or ''
        return f'<pre>{result}</pre>'


def render_form(url="", source="", default_repo='', collapse_code=False, *, app) -> str:
    """Allows selecting GitHub link or write source"""
    collapse_source = "collapseSource();" if collapse_code else ""

    js_content = """
    <script>
    var collapsible_code_elements = document.getElementsByClassName("jp-Editor");

    function onload() {
        collapsible_code_elements = document.getElementsByClassName("jp-Editor");
        for(let elem of collapsible_code_elements) {
            let e = elem;
            e.addEventListener('dblclick', function(event){e.classList.toggle('collapsed-input');});
        };
        var output_images = document.querySelectorAll(".jp-RenderedImage img");
        for(let elem of output_images) {
            let e = elem;
            e.addEventListener('dblclick', function(event){console.log(e); e.classList.toggle('full-width-image');});
        };
        // collapse_code_insertion
    };
    window.addEventListener('load', onload);
    function collapseSource() {
        for(let elem of collapsible_code_elements) {
            console.log('collapsing', elem);
            elem.classList.add('collapsed-input');
        }
    };
    function showSource() {
        for(let elem of collapsible_code_elements) {
            console.log('un-collapsing', elem);
            elem.classList.remove('collapsed-input');
        }
    };
    </script>
    """.replace('// collapse_code_insertion', collapse_source)

    return f"""
    <div style='margin-bottom: 15px;'>
        <label for='nothing_just_spacer' style='width: 170px; display: inline-block;'></label>
        {make_button_to_get_current_link()}
        &nbsp;
        <button type="button" onclick="collapseSource()">minimize code</button>
        &nbsp;
        <button type="button" onclick="showSource()">maximize code</button>
        &nbsp;
        Double click on input to minimize/maximize individual code input
    </div>
    <form action="{app.url_path_for('read_github')}" method='get'>
      <label for='github_permalink' style='width: 170px; display: inline-block;'>Github permalink</label>
      <input type="text" id="github_permalink" name="github_permalink" value="{html.escape(url)}" size=100 >
      <input type="submit" value="Submit">
    </form>
    <form action="{app.url_path_for('read_source')}" method='get'>
      <label for='github_permalink' style='width: 170px; display: inline-block;' >Or source code:</label>
      <textarea id="source" name="source" rows="4" cols="100"  style='vertical-align: top;'>{html.escape(source)}</textarea>
      <input type="submit" value="Submit">
    </form>
    <form action="{app.url_path_for('list_github')}" method='get'>
      <label for='repo' style='width: 170px; display: inline-block;' >Or repository:</label>
      <input type="text" id="repo" name="repo" value="{default_repo}" size=100 >
      <input type="submit" value="Submit">
    </form>    
    
    {js_content}
    """


def make_link(app, method, **kargs) -> str:
    from urllib.parse import urlencode
    return app.url_path_for(method) + '?' + urlencode(kargs)


def convert_newpy_text_to_html(source: str):
    with tempfile.TemporaryDirectory() as f:
        # copy config
        # with Path(f).joinpath(".newpyter_config.toml").open("w", encoding="utf-8") as ftarget:
        #     ftarget.write(newpyter_config_contents)

        local_path = Path(f).joinpath("nb.newpy")
        with local_path.open("w") as nbf:
            nbf.write(source)

        manager = NewpyterContentsManager()
        manager.root_dir = "/"
        old_local_path = local_path
        local_path = old_local_path.with_suffix(".ipynb")
        manager.convert_from_newpy_to_ipynb_or_reverse(str(old_local_path.absolute()), str(local_path.absolute()))

        html_exporter = HTMLExporter()
        html_exporter.template_name = "classic"

        # 3. Process the notebook we loaded earlier
        (body, resources) = html_exporter.from_filename(
            str(local_path),
        )
        return body


def make_button_to_get_current_link() -> str:
    return """
    <button onclick="copyToClip(document.getElementById('div-with-link').innerHTML)">Copy link to this page</button>
    <div id="div-with-link" style="display:none">
        <a id='link_to_viewer' href=''>newpy viewer</a>
    </div>
    <script>
        document.getElementById('link_to_viewer').href = window.location.href;
        function copyToClip(str) {
          function listener(e) {
            e.clipboardData.setData("text/html", str);
            e.clipboardData.setData("text/plain", str);
            e.preventDefault();
          }
          document.addEventListener("copy", listener);
          document.execCommand("copy");
          document.removeEventListener("copy", listener);
        };
    </script>
    """


def download_and_convert(permalink: str, secret: str, newpyter_toml: Path) -> Tuple[str, str]:
    assert permalink.startswith("https://github.com/")
    organization, repository, _blob_, commit, *path = permalink[len("https://github.com/"):].split("/")

    with tempfile.TemporaryDirectory() as f:
        # copy config in case conversion is required
        with Path(f).joinpath(".newpyter_config.toml").open("w", encoding="utf-8") as ftarget:
            ftarget.write(newpyter_toml.read_text())

        local_path = Path(f).joinpath(path[-1])

        path_in_repo = "/".join(path)
        request_link = f"https://api.github.com/repos/{organization}/{repository}/contents/{path_in_repo}?ref={commit}"

        print(request_link)

        sh.curl(
            "-H",
            "Accept: application/vnd.github.v4.raw",
            "-H",
            f"Authorization: Bearer {secret}",
            L=request_link,
            o=local_path,
        )
        contents = open(local_path).read()

        print(contents)

        if '"message": "Not Found",' in contents:
            print(contents)
            return contents, ""

        if local_path.name.endswith(".newpy"):
            manager = NewpyterContentsManager()
            manager.root_dir = "/"
            # for some reason on mac m1 is does not work without allow_hidden
            manager.allow_hidden = True
            old_local_path = local_path
            local_path = old_local_path.with_suffix(".ipynb")
            # assert 0 == 1, old_local_path
            assert old_local_path.exists()
            manager.convert_from_newpy_to_ipynb_or_reverse(str(old_local_path.absolute()), str(local_path.absolute()))

        if local_path.name.endswith(".ipynb"):
            # 1. Instantiate the exporter. We use the `classic` template for now; we'll get into more details
            # later about how to customize the exporter further.
            html_exporter = HTMLExporter()
            html_exporter.template_name = "classic"

            # 2. Process the notebook we loaded earlier
            (body, resources) = html_exporter.from_filename(
                str(local_path),
            )
            return body, contents

        if local_path.name.endswith(".html"):
            return contents, ""

        raise NotImplementedError()


def download_and_render_link_list(github_token, repo, path_in_repo, *, app) -> Optional[str]:
    with tempfile.TemporaryDirectory() as d:
        local_path = Path(d).joinpath('contents')
        sh.curl(
            "-H",
            "Accept: application/vnd.github.v4.raw",
            "-H",
            f"Authorization: Bearer {github_token}",
            L=f'https://api.github.com/repos/{repo}/contents/{path_in_repo}',
            o=local_path,
        )
        file_contents = open(local_path).read()
        try:
            import json
            items_in_folder: list[dict] = json.loads(file_contents)
            items_in_folder = list(items_in_folder)
        except:
            return None

        assert len(items_in_folder) > 0

        result = ''
        if path_in_repo.endswith('/'):
            path_in_repo = path_in_repo[:-1]

        if path_in_repo != '':
            parent_path = str(Path(path_in_repo).parent)
            link = make_link(app, 'list_github', repo=repo, path_in_repo=parent_path)
            result += f'<a href="{link}">..</a> <br/>'

        for item in items_in_folder:
            name = item['name']
            if item['type'] == 'dir':
                link = make_link(app, 'list_github', repo=repo, path_in_repo=path_in_repo + '/' + name)
                result += f'<a href="{link}">{name}</a> <br/>'
            elif item['type'] == 'file':
                if name.endswith('.ipynb') or name.endswith('.newpy'):
                    link = make_link(app, 'read_github', github_permalink=item['html_url'])
                    result += f'<a href="{link}">{name}</a> <br/>'
                else:
                    # do not provide links for other files
                    result += f'{name} <br/>'
            else:
                result += f'{name} (unrecognized) <br/>'

            # import pprint
            # result += pprint.pformat(item) + '<br />'

        result = f'''
        <div style='margin: 200px 200px;'>
        <h2>{path_in_repo}</h2>
        <p style='font-size: 14px;'>{result}</p>
        </div>
        '''
        return result


