"""
Coursera Downloader Skill for Rhea-Noir
Download Coursera course materials using coursera-dl
"""
import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List


class CourseraSkill:
    """Skill for downloading Coursera courses using coursera-dl."""

    name = "coursera"
    version = "1.0.0"
    description = "Download Coursera courses, videos, subtitles, and materials"

    def __init__(self):
        self.default_resolution = "540p"

    def _get_credentials(self) -> Dict[str, str]:
        """Get Coursera credentials from environment."""
        cauth = os.getenv("COURSERA_CAUTH")
        if cauth:
            return {"cauth": cauth}

        user = os.getenv("COURSERA_USER")
        password = os.getenv("COURSERA_PASS")
        if user and password:
            return {"user": user, "password": password}

        return {}

    def _check_installed(self) -> bool:
        """Check if coursera-dl is installed."""
        return shutil.which("coursera-dl") is not None

    def _build_command(
        self,
        course_slug: str,
        output_dir: str = "./courses",
        video_resolution: str = "540p",
        section_filter: Optional[str] = None,
        lecture_filter: Optional[str] = None,
        file_formats: Optional[List[str]] = None,
        ignore_formats: Optional[List[str]] = None,
        subtitle_languages: Optional[List[str]] = None,
        download_quizzes: bool = False
    ) -> List[str]:
        """Build coursera-dl command."""
        cmd = ["coursera-dl"]

        # Add credentials
        creds = self._get_credentials()
        if "cauth" in creds:
            cmd.extend(["-ca", creds["cauth"]])
        elif "user" in creds:
            cmd.extend(["-u", creds["user"], "-p", creds["password"]])
        else:
            # Try netrc
            cmd.append("-n")

        # Output path
        cmd.extend(["--path", output_dir])

        # Video resolution
        cmd.extend(["--video-resolution", video_resolution])

        # Section filter (regex)
        if section_filter:
            cmd.extend(["-sf", section_filter])

        # Lecture filter (regex)
        if lecture_filter:
            cmd.extend(["-lf", lecture_filter])

        # File format filter
        if file_formats:
            for fmt in file_formats:
                cmd.extend(["-f", fmt])

        # Ignore formats
        if ignore_formats:
            cmd.extend(["--ignore-formats", ",".join(ignore_formats)])

        # Subtitle languages
        if subtitle_languages:
            cmd.extend(["--subtitle-language", ",".join(subtitle_languages)])

        # Download quizzes
        if download_quizzes:
            cmd.append("--download-quizzes")

        # Add course slug
        cmd.append(course_slug)

        return cmd

    def _success(self, data: Any) -> Dict:
        """Return success response."""
        return {"success": True, "data": data}

    def _error(self, message: str) -> Dict:
        """Return error response."""
        return {"success": False, "error": message}

    def _run_command(self, cmd: List[str], cwd: Optional[str] = None) -> Dict:
        """Execute coursera-dl command."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=3600  # 1 hour timeout for large courses
            )

            if result.returncode == 0:
                return self._success({
                    "message": "Download completed successfully",
                    "output": result.stdout
                })
            else:
                return self._error(f"Command failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            return self._error("Download timed out after 1 hour")
        except Exception as e:
            return self._error(str(e))

    def download_course(
        self,
        course_slug: str,
        output_dir: str = "./courses",
        video_resolution: str = "540p",
        section_filter: Optional[str] = None,
        lecture_filter: Optional[str] = None,
        download_quizzes: bool = False,
        subtitle_languages: Optional[List[str]] = None
    ) -> Dict:
        """
        Download full Coursera course.

        Args:
            course_slug: Course identifier (e.g., "machine-learning")
            output_dir: Directory to save course materials
            video_resolution: Video quality (360p, 540p, 720p)
            section_filter: Regex filter for sections/weeks
            lecture_filter: Regex filter for lecture names
            download_quizzes: Whether to download quiz content
            subtitle_languages: List of subtitle language codes

        Returns:
            Dict with download status
        """
        if not self._check_installed():
            return self._error("coursera-dl not installed. Run: pip install coursera-dl")

        creds = self._get_credentials()
        if not creds:
            return self._error(
                "No credentials found. Set COURSERA_CAUTH or COURSERA_USER/COURSERA_PASS"
            )

        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        cmd = self._build_command(
            course_slug=course_slug,
            output_dir=output_dir,
            video_resolution=video_resolution,
            section_filter=section_filter,
            lecture_filter=lecture_filter,
            download_quizzes=download_quizzes,
            subtitle_languages=subtitle_languages
        )

        result = self._run_command(cmd)
        if result["success"]:
            result["data"]["course"] = course_slug
            result["data"]["output_dir"] = output_dir
            result["data"]["resolution"] = video_resolution

        return result

    def download_videos_only(
        self,
        course_slug: str,
        output_dir: str = "./courses",
        video_resolution: str = "540p",
        section_filter: Optional[str] = None,
        lecture_filter: Optional[str] = None
    ) -> Dict:
        """
        Download only video files from a course.

        Args:
            course_slug: Course identifier
            output_dir: Directory to save videos
            video_resolution: Video quality
            section_filter: Regex filter for sections
            lecture_filter: Regex filter for lectures

        Returns:
            Dict with download status
        """
        if not self._check_installed():
            return self._error("coursera-dl not installed. Run: pip install coursera-dl")

        creds = self._get_credentials()
        if not creds:
            return self._error("No credentials found")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        cmd = self._build_command(
            course_slug=course_slug,
            output_dir=output_dir,
            video_resolution=video_resolution,
            section_filter=section_filter,
            lecture_filter=lecture_filter,
            file_formats=["mp4", "webm"]
        )

        result = self._run_command(cmd)
        if result["success"]:
            result["data"]["course"] = course_slug
            result["data"]["type"] = "videos_only"

        return result

    def download_subtitles(
        self,
        course_slug: str,
        output_dir: str = "./courses",
        languages: Optional[List[str]] = None
    ) -> Dict:
        """
        Download only subtitle files from a course.

        Args:
            course_slug: Course identifier
            output_dir: Directory to save subtitles
            languages: List of language codes (e.g., ["en", "es"])

        Returns:
            Dict with download status
        """
        if not self._check_installed():
            return self._error("coursera-dl not installed. Run: pip install coursera-dl")

        creds = self._get_credentials()
        if not creds:
            return self._error("No credentials found")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        cmd = self._build_command(
            course_slug=course_slug,
            output_dir=output_dir,
            ignore_formats=["mp4", "webm"],
            subtitle_languages=languages or ["en"]
        )

        result = self._run_command(cmd)
        if result["success"]:
            result["data"]["course"] = course_slug
            result["data"]["type"] = "subtitles_only"
            result["data"]["languages"] = languages or ["en"]

        return result

    def download_materials(
        self,
        course_slug: str,
        output_dir: str = "./courses",
        file_formats: Optional[List[str]] = None
    ) -> Dict:
        """
        Download supplementary materials (PDFs, slides, etc.).

        Args:
            course_slug: Course identifier
            output_dir: Directory to save materials
            file_formats: List of file formats (e.g., ["pdf", "ppt", "pptx"])

        Returns:
            Dict with download status
        """
        if not self._check_installed():
            return self._error("coursera-dl not installed. Run: pip install coursera-dl")

        creds = self._get_credentials()
        if not creds:
            return self._error("No credentials found")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        formats = file_formats or ["pdf", "ppt", "pptx", "doc", "docx"]

        cmd = self._build_command(
            course_slug=course_slug,
            output_dir=output_dir,
            file_formats=formats,
            ignore_formats=["mp4", "webm"]
        )

        result = self._run_command(cmd)
        if result["success"]:
            result["data"]["course"] = course_slug
            result["data"]["type"] = "materials"
            result["data"]["formats"] = formats

        return result


# Singleton instance
skill = CourseraSkill()
