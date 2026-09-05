# Kumar Robotics Website

## How to build locally
1. Install [Hugo](https://gohugo.io/installation/), extended edition.
2. Clone this repo `git clone --recurse-submodules -j8 https://github.com/KumarRobotics/kr_website.git`
3. `hugo server  -D --disableFastRender`

The website should be available at `http://localhost:1313/`.

## How to submit modifications
1. Build the website locally. See [notes above](#how-to-build-locally).
2. Modify the website and **verify your modifications**.
3. Submit a PR on Github. Please do not push directly to the `main` branch.

Content is located in the `content/` folder. Images are in `static/`.

## Automatic validation
After submitting a PR, there are a few checks that are performed:

### Image check
The [`Lint`](.github/workflows/lint.yml) workflow run on every pull
request (and locally with `python3 scripts/check_images.py`) enforces:
- Member photos (`static/img/group/current/`) must be **exactly 600x600 px**
  and at most **500 KB**.
- Every image referenced in `content/`, `data/` or `layouts/` must exist under
`static/`.

## Automated deployment to Pantheon

The website is deployed to Pantheon (static hosting via the Empty Upstream)
with the [`deploy-pantheon`](.github/workflows/deploy-pantheon.yml) workflow:

- Push to `dev` builds the site and deploys it to the **Test** environment.
- Push to `main` builds the site and deploys it through Test to **Live**.
