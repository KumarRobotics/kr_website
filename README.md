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

## Automated deployment to Pantheon

The website is deployed to Pantheon (static hosting via the Empty Upstream)
with the [`deploy-pantheon`](.github/workflows/deploy-pantheon.yml) workflow:

- Push to `dev` builds the site and deploys it to the **Test** environment.
- Push to `main` builds the site and deploys it through Test to **Live**.
