"""Build threat relationship graph linking APK, IOCs, certs, and behaviors."""

from typing import Any, Dict, List
import hashlib

from app.utils.safe_data import safe_dict, safe_list, safe_str_list


def build_threat_graph(
    apk_id: str,
    filename: str,
    file_hash: str,
    findings: Dict[str, Any],
    mitre_mappings: List[Dict[str, Any]],
) -> Dict[str, Any]:
    nodes: List[Dict[str, Any]] = [
        {
            "id": f"apk:{apk_id}",
            "type": "apk",
            "label": filename,
            "data": {
                "hash": file_hash,
                "package": safe_dict(findings.get("metadata")).get("package_name"),
            },
        }
    ]
    edges: List[Dict[str, Any]] = []

    def add_node(node_id: str, ntype: str, label: str, data: Dict | None = None) -> str:
        if not any(n["id"] == node_id for n in nodes):
            nodes.append({"id": node_id, "type": ntype, "label": label, "data": data or {}})
        return node_id

    for perm in safe_str_list(findings.get("permissions"))[:15]:
        pid = f"perm:{hashlib.md5(perm.encode()).hexdigest()[:8]}"
        add_node(pid, "permission", perm.split(".")[-1], {"full": perm})
        edges.append({"source": f"apk:{apk_id}", "target": pid, "type": "requests"})

    for url in safe_str_list(findings.get("urls"))[:10]:
        uid = f"url:{hashlib.md5(url.encode()).hexdigest()[:8]}"
        add_node(uid, "url", url[:48], {"url": url})
        edges.append({"source": f"apk:{apk_id}", "target": uid, "type": "embeds"})

    for ip in safe_str_list(findings.get("ips"))[:8]:
        iid = f"ip:{ip}"
        add_node(iid, "ip", ip, {})
        edges.append({"source": f"apk:{apk_id}", "target": iid, "type": "contacts"})

    for cert in safe_list(findings.get("certificates"))[:5]:
        if not isinstance(cert, dict):
            continue
        subject = str(cert.get("subject") or "Certificate")
        sha = cert.get("sha256") or cert.get("subject") or "unknown"
        cid = f"cert:{str(sha)[:16]}"
        add_node(cid, "certificate", subject[:40], cert)
        edges.append({"source": f"apk:{apk_id}", "target": cid, "type": "signed_with"})

    for m in mitre_mappings[:12]:
        if not isinstance(m, dict):
            continue
        technique = str(m.get("technique") or "Unknown technique")
        mid = f"mitre:{technique.replace(' ', '_')[:24]}"
        add_node(mid, "technique", technique, m)
        edges.append({"source": f"apk:{apk_id}", "target": mid, "type": "exhibits"})

    family = findings.get("malware_family_hint")
    if family:
        fid = f"family:{family}"
        add_node(fid, "malware_family", family, {})
        edges.append({"source": f"apk:{apk_id}", "target": fid, "type": "classified_as"})

    return {"nodes": nodes, "edges": edges}
