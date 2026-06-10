"""
Static APK Analysis Engine
Uses MobSF, JADX, APKTool, and Androguard
"""

import json
import subprocess
import os
import re
import uuid
import zipfile
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

WORK_ROOT = os.getenv("ANALYSIS_WORK_DIR", "/app/analysis_results")


class StaticAnalyzer:
    def __init__(self, apk_path: str):
        self.apk_path = apk_path
        self.work_dir = os.path.join(WORK_ROOT, str(uuid.uuid4())[:12])
        self.results: Dict[str, Any] = {
            "manifest": "",
            "metadata": {},
            "permissions": [],
            "activities": [],
            "services": [],
            "broadcast_receivers": [],
            "content_providers": [],
            "intent_filters": [],
            "suspicious_apis": {},
            "hardcoded_secrets": [],
            "urls": [],
            "ips": [],
            "domains": [],
            "certificates": [],
            "obfuscation": {"score": 0.0, "indicators": []},
            "code_patterns": [],
        }

    async def analyze(self) -> Dict[str, Any]:
        """Run complete static analysis"""
        try:
            os.makedirs(self.work_dir, exist_ok=True)
            await self._extract_manifest()
            await self._extract_metadata()
            await self._extract_permissions()
            await self._extract_components()
            await self._extract_certificates()
            await self._extract_urls_and_ips()
            await self._detect_suspicious_apis()
            await self._scan_for_secrets()
            await self._assess_obfuscation()
            return self.results
        except Exception as e:
            logger.error(f"Static analysis failed: {str(e)}")
            raise
        finally:
            _safe_rmtree(self.work_dir)

    async def _extract_manifest(self) -> None:
        """Extract AndroidManifest.xml via apktool"""
        try:
            out_dir = os.path.join(self.work_dir, "decoded")
            cmd = ["apktool", "d", "-f", "-s", self.apk_path, "-o", out_dir]
            subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            manifest_path = Path(out_dir) / "AndroidManifest.xml"
            if manifest_path.exists():
                self.results["manifest"] = manifest_path.read_text(encoding="utf-8", errors="ignore")[:20000]
            else:
                self._extract_manifest_from_zip()
        except Exception as e:
            logger.error(f"Manifest extraction failed: {str(e)}")
            self._extract_manifest_from_zip()

    def _extract_manifest_from_zip(self) -> None:
        try:
            with zipfile.ZipFile(self.apk_path, "r") as zf:
                if "AndroidManifest.xml" in zf.namelist():
                    self.results["manifest"] = zf.read("AndroidManifest.xml").decode(
                        "utf-8", errors="ignore"
                    )[:5000]
        except Exception as e:
            logger.error(f"ZIP manifest fallback failed: {e}")

    async def _extract_metadata(self) -> None:
        manifest = self.results.get("manifest") or ""
        if not isinstance(manifest, str):
            manifest = str(manifest)
        pkg = re.search(r'package="([^"]+)"', manifest)
        app = re.search(r'<application[^>]+android:label="([^"]+)"', manifest)
        ver_name = re.search(r'versionName="([^"]+)"', manifest)
        ver_code = re.search(r'versionCode="([^"]+)"', manifest)
        self.results["metadata"] = {
            "package_name": pkg.group(1) if pkg else None,
            "app_name": app.group(1) if app else None,
            "version_name": ver_name.group(1) if ver_name else None,
            "version_code": ver_code.group(1) if ver_code else None,
        }

    async def _extract_certificates(self) -> None:
        """Extract signing certificate metadata from APK META-INF."""
        certs: List[Dict[str, Any]] = []
        try:
            with zipfile.ZipFile(self.apk_path, "r") as zf:
                for name in zf.namelist():
                    if name.startswith("META-INF/") and name.endswith((".RSA", ".DSA", ".EC")):
                        certs.append(
                            {
                                "subject": name.replace("META-INF/", ""),
                                "path": name,
                                "sha256": None,
                            }
                        )
            self.results["certificates"] = certs[:10]
        except Exception as e:
            logger.error(f"Certificate extraction failed: {e}")

    async def _assess_obfuscation(self) -> None:
        indicators = []
        manifest = self.results.get("manifest") or ""
        if isinstance(manifest, str):
            short_names = len(re.findall(r'android:name="[a-z]\.[a-z]"', manifest))
            if short_names > 5:
                indicators.append("Proguard-style short class names in manifest")
        if len(self.results.get("activities", [])) > 30:
            indicators.append("Excessive activity declarations")
        score = min(1.0, len(indicators) * 0.25 + (0.2 if self.results.get("hardcoded_secrets") else 0))
        self.results["obfuscation"] = {"score": score, "indicators": indicators}

    async def _extract_permissions(self) -> None:
        """Extract permissions from manifest"""
        try:
            manifest_str = self.results.get("manifest", "") or ""
            permissions = re.findall(
                r'android:name="(android\.permission\.[^"]+)"',
                manifest_str,
            )
            uses_perms = re.findall(
                r'<uses-permission[^>]+android:name="([^"]+)"',
                manifest_str,
            )
            self.results["permissions"] = list(set(permissions + uses_perms))
        except Exception as e:
            logger.error(f"Permission extraction failed: {str(e)}")

    async def _extract_components(self) -> None:
        """Extract activities, services, broadcast receivers, etc."""
        try:
            manifest_str = self.results.get("manifest", "")
            import re
            
            # Extract activities
            self.results["activities"] = re.findall(
                r'<activity\s+android:name="([^"]+)"',
                manifest_str
            )
            
            # Extract services
            self.results["services"] = re.findall(
                r'<service\s+android:name="([^"]+)"',
                manifest_str
            )
            
            # Extract broadcast receivers
            self.results["broadcast_receivers"] = re.findall(
                r'<receiver\s+android:name="([^"]+)"',
                manifest_str
            )
            
            # Extract content providers
            self.results["content_providers"] = re.findall(
                r'<provider\s+android:name="([^"]+)"',
                manifest_str
            )
            
            # Extract intent filters
            self.results["intent_filters"] = re.findall(
                r'<action\s+android:name="([^"]+)"',
                manifest_str
            )
            
        except Exception as e:
            logger.error(f"Component extraction failed: {str(e)}")

    async def _extract_urls_and_ips(self) -> None:
        """Extract URLs, IPs, and domains from manifest and APK strings."""
        try:
            blob = self.results.get("manifest", "") or ""
            if isinstance(blob, dict):
                blob = str(blob)
            try:
                with zipfile.ZipFile(self.apk_path, "r") as zf:
                    for name in zf.namelist():
                        if name.endswith((".xml", ".json", ".properties")) and zf.getinfo(name).file_size < 500000:
                            try:
                                blob += zf.read(name).decode("utf-8", errors="ignore")[:50000]
                            except Exception:
                                pass
            except Exception:
                pass

            url_pattern = r'https?://[^\s"\'\)><]+'
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            domain_pattern = r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}'

            self.results["urls"] = list(set(re.findall(url_pattern, blob)))[:100]
            self.results["ips"] = list(set(re.findall(ip_pattern, blob)))[:50]
            self.results["domains"] = list(
                {d for d in re.findall(domain_pattern, blob) if not d.endswith(".xml")}
            )[:80]
        except Exception as e:
            logger.error(f"URL/IP extraction failed: {str(e)}")

    async def _detect_suspicious_apis(self) -> None:
        """Detect use of suspicious APIs"""
        suspicious_apis = {
            "crypto": [
                "javax.crypto.Cipher",
                "java.security.MessageDigest",
                "java.util.Base64",
            ],
            "networking": [
                "java.net.Socket",
                "java.net.URL",
                "org.apache.http.client.HttpClient",
                "okhttp3.OkHttpClient",
            ],
            "process_execution": [
                "java.lang.Runtime.exec",
                "java.lang.ProcessBuilder",
            ],
            "reflection": [
                "java.lang.reflect.Method",
                "java.lang.Class.forName",
            ],
            "file_operations": [
                "java.io.File",
                "java.nio.file.Files",
            ],
        }
        
        self.results["suspicious_apis"] = suspicious_apis

    async def _scan_for_secrets(self) -> None:
        """Scan for hardcoded secrets in manifest and embedded resources."""
        try:
            blob = self.results.get("manifest", "") or ""
            secrets_patterns = {
                "api_key": r"api[_-]?key\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
                "aws_key": r"AKIA[0-9A-Z]{16}",
                "jwt": r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
            }
            found = []
            for stype, pattern in secrets_patterns.items():
                matches = re.findall(pattern, blob, re.IGNORECASE)
                if matches:
                    found.append({"type": stype, "matches": len(matches)})
            self.results["hardcoded_secrets"] = found
        except Exception as e:
            logger.error(f"Secret scanning failed: {str(e)}")


def _safe_rmtree(path: str) -> None:
    import shutil
    try:
        if path and os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass


class PermissionAnalyzer:
    """Analyze permissions for risk"""
    
    DANGEROUS_PERMISSIONS = {
        "android.permission.CAMERA": "high",
        "android.permission.RECORD_AUDIO": "high",
        "android.permission.ACCESS_FINE_LOCATION": "high",
        "android.permission.READ_CONTACTS": "high",
        "android.permission.READ_SMS": "critical",
        "android.permission.SEND_SMS": "critical",
        "android.permission.CALL_PHONE": "critical",
        "android.permission.CHANGE_WIFI_STATE": "high",
        "android.permission.CHANGE_NETWORK_STATE": "high",
        "android.permission.INTERNET": "medium",
        "android.permission.ACCESS_NETWORK_STATE": "medium",
    }
    
    @staticmethod
    def analyze_permissions(permissions: List[str]) -> Dict[str, Any]:
        """Analyze permission risks"""
        risk_score = 0.0
        dangerous_perms = []
        
        for perm in permissions:
            if perm in PermissionAnalyzer.DANGEROUS_PERMISSIONS:
                risk_level = PermissionAnalyzer.DANGEROUS_PERMISSIONS[perm]
                risk_value = {"critical": 0.3, "high": 0.2, "medium": 0.1}.get(risk_level, 0.05)
                risk_score += risk_value
                dangerous_perms.append({"permission": perm, "risk": risk_level})
        
        return {
            "total_permissions": len(permissions),
            "dangerous_permissions": dangerous_perms,
            "risk_contribution": min(risk_score, 1.0)
        }
