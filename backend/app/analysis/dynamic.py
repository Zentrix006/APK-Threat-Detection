"""
Dynamic APK Analysis Engine
Uses Android Emulator, Frida, ADB, and tcpdump
"""

import subprocess
import os
import json
import asyncio
from typing import Dict, List, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DynamicAnalyzer:
    def __init__(self, apk_path: str, package_name: str):
        self.apk_path = apk_path
        self.package_name = package_name
        self.device_id = os.getenv("EMULATOR_HOST", "emulator-5554")
        self.results = {
            "network_traffic": [],
            "api_calls": [],
            "file_operations": [],
            "launched_activities": [],
            "c2_communications": [],
            "dns_queries": [],
        }

    async def analyze(self) -> Dict[str, Any]:
        """Run complete dynamic analysis"""
        try:
            # Check if device/emulator is available
            if not await self._check_device():
                logger.warning("Android device/emulator not available, skipping dynamic analysis")
                return self.results
            
            await self._install_apk()
            
            # Run analysis in parallel
            tasks = [
                self._capture_network_traffic(),
                self._instrument_with_frida(),
                self._monitor_file_operations(),
                self._capture_activities(),
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            await self._cleanup()
            return self.results
            
        except Exception as e:
            logger.error(f"Dynamic analysis failed: {str(e)}")
            return self.results

    async def _check_device(self) -> bool:
        """Check if device is available"""
        try:
            result = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return "device" in result.stdout
        except:
            return False

    async def _install_apk(self) -> None:
        """Install APK on emulator/device"""
        try:
            cmd = ["adb", "-s", self.device_id, "install", "-r", self.apk_path]
            subprocess.run(cmd, capture_output=True, timeout=60)
            logger.info(f"Installed {self.package_name}")
        except Exception as e:
            logger.error(f"APK installation failed: {str(e)}")

    async def _capture_network_traffic(self) -> None:
        """Capture network traffic using tcpdump"""
        try:
            # Start tcpdump on device
            cmd = ["adb", "-s", self.device_id, "shell", "tcpdump", "-i", "any", "-w", "/data/local/tmp/traffic.pcap"]
            
            # Run for 30 seconds
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            await asyncio.sleep(30)
            process.terminate()
            
            # Pull the capture file
            subprocess.run(
                ["adb", "-s", self.device_id, "pull", "/data/local/tmp/traffic.pcap", "/tmp/traffic.pcap"],
                capture_output=True
            )
            
            # Parse PCAP file for interesting traffic
            self.results["network_traffic"] = await self._parse_pcap("/tmp/traffic.pcap")
            
        except Exception as e:
            logger.error(f"Network capture failed: {str(e)}")

    async def _parse_pcap(self, pcap_path: str) -> List[Dict]:
        """Parse PCAP file for network connections"""
        try:
            # Use scapy to parse PCAP
            from scapy.all import rdpcap, IP, TCP, UDP
            
            packets = rdpcap(pcap_path)
            connections = []
            
            for packet in packets:
                if IP in packet:
                    src_ip = packet[IP].src
                    dst_ip = packet[IP].dst
                    
                    if TCP in packet:
                        connections.append({
                            "type": "TCP",
                            "src_ip": src_ip,
                            "dst_ip": dst_ip,
                            "src_port": packet[TCP].sport,
                            "dst_port": packet[TCP].dport,
                            "timestamp": datetime.now().isoformat(),
                        })
                    elif UDP in packet:
                        connections.append({
                            "type": "UDP",
                            "src_ip": src_ip,
                            "dst_ip": dst_ip,
                            "src_port": packet[UDP].sport,
                            "dst_port": packet[UDP].dport,
                            "timestamp": datetime.now().isoformat(),
                        })
            
            return connections
        except Exception as e:
            logger.error(f"PCAP parsing failed: {str(e)}")
            return []

    async def _instrument_with_frida(self) -> None:
        """Use Frida to instrument the app and capture API calls"""
        try:
            frida_script = """
            Java.perform(function() {
                var Runtime = Java.use("java.lang.Runtime");
                Runtime.exec.overload('[Ljava/lang/String;').implementation = function(command) {
                    console.log("[*] Runtime.exec called with: " + command);
                    return this.exec(command);
                };
                
                var URL = Java.use("java.net.URL");
                URL.$init.overload('java.lang.String').implementation = function(str) {
                    console.log("[*] URL created: " + str);
                    return this.$init(str);
                };
            });
            """
            
            cmd = [
                "frida",
                "-U",
                "-n",
                self.package_name,
                "-l",
                "/tmp/frida_script.js"
            ]
            
            with open("/tmp/frida_script.js", "w") as f:
                f.write(frida_script)
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Let Frida run for 30 seconds
            await asyncio.sleep(30)
            process.terminate()
            
            # Parse Frida output
            stdout, _ = process.communicate()
            self.results["api_calls"] = await self._parse_frida_output(stdout)
            
        except Exception as e:
            logger.error(f"Frida instrumentation failed: {str(e)}")

    async def _parse_frida_output(self, output: str) -> List[Dict]:
        """Parse Frida output for API calls"""
        api_calls = []
        for line in output.split("\n"):
            if "[*]" in line:
                api_calls.append({"call": line.strip()})
        return api_calls

    async def _monitor_file_operations(self) -> None:
        """Monitor file operations"""
        try:
            # Check app's data directory
            cmd = ["adb", "-s", self.device_id, "shell", "find", f"/data/data/{self.package_name}", "-type", "f"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            files = result.stdout.strip().split("\n")
            self.results["file_operations"] = [
                {"file": f, "size": "unknown"} for f in files if f
            ][:10]  # Limit to first 10
            
        except Exception as e:
            logger.error(f"File monitoring failed: {str(e)}")

    async def _capture_activities(self) -> None:
        """Capture launched activities"""
        try:
            # Start the app
            cmd = ["adb", "-s", self.device_id, "shell", "am", "start", "-n", f"{self.package_name}/.MainActivity"]
            subprocess.run(cmd, capture_output=True, timeout=10)
            
            # Wait a bit for activity to start
            await asyncio.sleep(5)
            
            # Get current foreground activity
            cmd = ["adb", "-s", self.device_id, "shell", "dumpsys", "window", "windows"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse for the current activity
            for line in result.stdout.split("\n"):
                if "mCurrentFocus" in line:
                    self.results["launched_activities"].append({"activity": line.strip()})
            
        except Exception as e:
            logger.error(f"Activity capture failed: {str(e)}")

    async def _cleanup(self) -> None:
        """Clean up after analysis"""
        try:
            # Uninstall app
            cmd = ["adb", "-s", self.device_id, "uninstall", self.package_name]
            subprocess.run(cmd, capture_output=True, timeout=30)
        except:
            pass


class C2Detector:
    """Detect Command & Control communications"""
    
    # Known C2 domains and IPs
    KNOWN_C2_INDICATORS = {
        "domains": [
            ".*\.top",
            ".*\.tk",
            ".*\.ml",
            ".*\.ga",
        ],
        "ips": [
            "0.0.0.0",
            "127.0.0.1",
        ],
        "ports": [4444, 5555, 6666, 7777, 8888, 9999],
    }
    
    @staticmethod
    def detect_c2(network_traffic: List[Dict], urls: List[str]) -> List[Dict]:
        """Detect potential C2 communications"""
        c2_communications = []
        
        import re
        
        for url in urls:
            for pattern in C2Detector.KNOWN_C2_INDICATORS["domains"]:
                if re.match(pattern, url):
                    c2_communications.append({
                        "type": "C2",
                        "indicator": url,
                        "indicator_type": "domain",
                        "confidence": 0.7,
                    })
        
        # Check network traffic for suspicious ports
        for traffic in network_traffic:
            if traffic.get("dst_port") in C2Detector.KNOWN_C2_INDICATORS["ports"]:
                c2_communications.append({
                    "type": "C2",
                    "indicator": traffic.get("dst_ip"),
                    "port": traffic.get("dst_port"),
                    "indicator_type": "ip_port",
                    "confidence": 0.6,
                })
        
        return c2_communications
