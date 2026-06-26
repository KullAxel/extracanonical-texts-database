#!/usr/bin/env python3
from pathlib import Path
import sys, json
try:
    import yaml
except ModuleNotFoundError:
    yaml = None
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'texts.yaml'
JSON_DATA = ROOT / 'data' / 'texts.json'
REQUIRED = ['id','title_standard','title_alternatives','category','approximate_date','date_confidence','date_evidence','surviving_languages','manuscript_witnesses','primary_community_or_tradition','key_content_summary','evidence_of_historical_popularity_or_use','canonical_status_by_tradition','reasons_excluded_or_marginalized','relationship_to_canonical_texts','related_texts','modern_editions_translations_digital_access','scholarly_notes','sources']
STATUS_FIELDS = ['jewish_tanakh','protestant_ot_or_nt','roman_catholic','eastern_orthodox','oriental_orthodox','ethiopian_orthodox','other_notes']
SOURCE_FIELDS = ['title','author_or_institution','url_or_citation','reliability_type']
VALID_CONF = {'high','medium-high','medium','low-medium','low'}
VALID_REL = {'primary','manuscript_catalog','critical_edition','academic_reference','secondary_summary'}

def fail(msg):
    print(f'ERROR: {msg}')
    return 1

def main():
    if yaml is not None and DATA.exists():
        obj = yaml.safe_load(DATA.read_text())
    else:
        obj = json.loads(JSON_DATA.read_text())
    texts = obj.get('texts') or []
    cats = set(obj.get('metadata',{}).get('controlled_categories') or [])
    ids = set(); errors=[]
    for i,e in enumerate(texts,1):
        eid=e.get('id',f'#{i}')
        for k in REQUIRED:
            if k not in e:
                errors.append(f'{eid}: missing field {k}')
            elif e[k] in (None,'') and k not in {'title_alternatives','related_texts'}:
                errors.append(f'{eid}: empty field {k}')
        if eid in ids: errors.append(f'{eid}: duplicate id')
        ids.add(eid)
        if e.get('category') not in cats: errors.append(f'{eid}: category not in controlled list: {e.get("category")}')
        if e.get('date_confidence') not in VALID_CONF: errors.append(f'{eid}: invalid date_confidence {e.get("date_confidence")}')
        st=e.get('canonical_status_by_tradition') or {}
        for k in STATUS_FIELDS:
            if not st.get(k): errors.append(f'{eid}: canonical_status_by_tradition missing/empty {k}')
        srcs=e.get('sources') or []
        if not srcs: errors.append(f'{eid}: no sources')
        for j,s in enumerate(srcs,1):
            for k in SOURCE_FIELDS:
                if not s.get(k): errors.append(f'{eid}: source {j} missing/empty {k}')
            if s.get('reliability_type') not in VALID_REL:
                errors.append(f'{eid}: source {j} invalid reliability_type {s.get("reliability_type")}')
    if errors:
        print('\n'.join(errors))
        print(f'FAILED validation: {len(errors)} error(s) across {len(texts)} entries')
        return 1
    print(f'OK: {len(texts)} entries; {len(ids)} unique IDs; {len(cats)} controlled categories; all required fields and sources present.')
    return 0
if __name__ == '__main__':
    sys.exit(main())
