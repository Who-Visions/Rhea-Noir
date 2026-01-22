"""
Gallery-DL Skill for Rhea-Noir
Download images from 100+ gallery sites
"""
import os
import subprocess
import shutil
import json
from pathlib import Path
from typing import Optional, Dict, Any, List


class GalleryDLSkill:
    """Skill for downloading images using gallery-dl."""

    name = "gallerydl"
    version = "1.0.0"
    description = "Download images and galleries from 100+ image hosting sites"

    def __init__(self):
        self.default_template = "{category}/{subcategory}/{filename}.{extension}"

    def _check_installed(self) -> bool:
        """Check if gallery-dl is installed."""
        return shutil.which("gallery-dl") is not None

    def _success(self, data: Any) -> Dict:
        """Return success response."""
        return {"success": True, "data": data}

    def _error(self, message: str) -> Dict:
        """Return error response."""
        return {"success": False, "error": message}

    def _build_command(
        self,
        url: str,
        output_dir: str = "./gallery",
        output_template: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        cookies_from: Optional[str] = None,
        limit: Optional[int] = None,
        get_urls_only: bool = False,
        file_types: Optional[List[str]] = None,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        chapter_filter: Optional[str] = None
    ) -> List[str]:
        """Build gallery-dl command."""
        cmd = ["gallery-dl"]

        # Output directory
        cmd.extend(["-d", output_dir])

        # Output template
        if output_template:
            cmd.extend(["-o", f"filename={output_template}"])

        # Authentication
        user = username or os.getenv("GALLERY_DL_USER")
        pwd = password or os.getenv("GALLERY_DL_PASS")
        if user and pwd:
            cmd.extend(["-u", user, "-p", pwd])

        # Browser cookies
        if cookies_from:
            cmd.extend(["--cookies-from-browser", cookies_from])

        # Limit downloads
        if limit:
            cmd.extend(["--range", f"1-{limit}"])

        # Get URLs only (no download)
        if get_urls_only:
            cmd.append("-g")

        # File type filter
        if file_types:
            filter_expr = " or ".join([f"extension == '{t}'" for t in file_types])
            cmd.extend(["--filter", filter_expr])

        # Size filters
        if min_width:
            cmd.extend(["--filter", f"width >= {min_width}"])
        if min_height:
            cmd.extend(["--filter", f"height >= {min_height}"])

        # Chapter filter (for manga)
        if chapter_filter:
            cmd.extend(["--chapter-filter", chapter_filter])

        # Add URL
        cmd.append(url)

        return cmd

    def _run_command(
        self,
        cmd: List[str],
        capture_output: bool = True,
        timeout: int = 3600
    ) -> Dict:
        """Execute gallery-dl command."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0:
                output = result.stdout if capture_output else "Download completed"
                return self._success({
                    "message": "Download completed successfully",
                    "output": output
                })
            else:
                return self._error(f"Command failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            return self._error(f"Download timed out after {timeout} seconds")
        except Exception as e:
            return self._error(str(e))

    def download_gallery(
        self,
        url: str,
        output_dir: str = "./gallery",
        output_template: Optional[str] = None,
        cookies_from: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict:
        """
        Download images from a gallery URL.

        Args:
            url: Gallery URL
            output_dir: Directory to save images
            output_template: Custom filename template
            cookies_from: Browser to get cookies from (firefox, chrome, etc.)
            limit: Maximum number of images to download

        Returns:
            Dict with download status
        """
        if not self._check_installed():
            return self._error("gallery-dl not installed. Run: pip install gallery-dl")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        cmd = self._build_command(
            url=url,
            output_dir=output_dir,
            output_template=output_template,
            cookies_from=cookies_from,
            limit=limit
        )

        result = self._run_command(cmd)
        if result["success"]:
            result["data"]["url"] = url
            result["data"]["output_dir"] = output_dir

        return result

    def download_user(
        self,
        url: str,
        output_dir: str = "./gallery",
        cookies_from: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict:
        """
        Download all images from a user/artist.

        Args:
            url: User profile URL
            output_dir: Directory to save images
            cookies_from: Browser to get cookies from
            limit: Maximum number of images

        Returns:
            Dict with download status
        """
        if not self._check_installed():
            return self._error("gallery-dl not installed. Run: pip install gallery-dl")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        cmd = self._build_command(
            url=url,
            output_dir=output_dir,
            cookies_from=cookies_from,
            limit=limit
        )

        result = self._run_command(cmd)
        if result["success"]:
            result["data"]["type"] = "user_download"
            result["data"]["url"] = url

        return result

    def get_urls(self, url: str, limit: Optional[int] = None) -> Dict:
        """
        Get direct image URLs without downloading.

        Args:
            url: Gallery or post URL
            limit: Maximum number of URLs to return

        Returns:
            Dict with list of image URLs
        """
        if not self._check_installed():
            return self._error("gallery-dl not installed. Run: pip install gallery-dl")

        cmd = self._build_command(
            url=url,
            output_dir=".",
            get_urls_only=True,
            limit=limit
        )

        result = self._run_command(cmd)
        if result["success"]:
            # Parse URLs from output
            urls = [line.strip() for line in result["data"]["output"].split("\n") if line.strip()]
            result["data"] = {
                "urls": urls,
                "count": len(urls),
                "source": url
            }

        return result

    def download_with_filter(
        self,
        url: str,
        output_dir: str = "./gallery",
        file_types: Optional[List[str]] = None,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        limit: Optional[int] = None,
        cookies_from: Optional[str] = None
    ) -> Dict:
        """
        Download images with content filtering.

        Args:
            url: Gallery URL
            output_dir: Directory to save images
            file_types: List of allowed extensions (jpg, png, gif, webp)
            min_width: Minimum image width
            min_height: Minimum image height
            limit: Maximum number of images
            cookies_from: Browser to get cookies from

        Returns:
            Dict with download status
        """
        if not self._check_installed():
            return self._error("gallery-dl not installed. Run: pip install gallery-dl")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        cmd = self._build_command(
            url=url,
            output_dir=output_dir,
            file_types=file_types,
            min_width=min_width,
            min_height=min_height,
            limit=limit,
            cookies_from=cookies_from
        )

        result = self._run_command(cmd)
        if result["success"]:
            result["data"]["url"] = url
            result["data"]["filters"] = {
                "file_types": file_types,
                "min_width": min_width,
                "min_height": min_height
            }

        return result

    def download_manga(
        self,
        url: str,
        output_dir: str = "./manga",
        chapter_filter: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict:
        """
        Download manga chapters.

        Args:
            url: Manga URL (MangaDex, Webtoon, etc.)
            output_dir: Directory to save chapters
            chapter_filter: Filter expression (e.g., "10 <= chapter < 20")
            language: Language code (e.g., "en", "jp")

        Returns:
            Dict with download status
        """
        if not self._check_installed():
            return self._error("gallery-dl not installed. Run: pip install gallery-dl")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        cmd = ["gallery-dl", "-d", output_dir]

        if chapter_filter:
            cmd.extend(["--chapter-filter", chapter_filter])

        if language:
            cmd.extend(["-o", f"lang={language}"])

        cmd.append(url)

        result = self._run_command(cmd)
        if result["success"]:
            result["data"]["url"] = url
            result["data"]["type"] = "manga"
            if chapter_filter:
                result["data"]["chapter_filter"] = chapter_filter

        return result


# Singleton instance
skill = GalleryDLSkill()
