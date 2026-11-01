"""Freeze the trivium batch from imported Latin and explicit print corrections."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'batches/002-trivium'


def main():
    TARGET.mkdir(parents=True,exist_ok=True)
    records={}
    hashes={}
    for book in [1,2]:
        path=ROOT/f'latin/book-{book:02}.jsonl'
        hashes[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
        for line in path.read_text(encoding='utf-8').splitlines():
            row=json.loads(line); records[row['ref']]=row['text']
    first,second=records['2.1.1'].split(' 2 Coniuncta',1)
    records['2.1.1']=first
    records['2.1.2']='Coniuncta'+second
    fixes=[
        ('2.1.1','eloquentia copia','[eloquentia copia]','Lindsay brackets this phrase; volume I PDF page 95.'),
        ('2.1.1','ῥητορίζειν','ῥητορεύειν','Restore the printed Greek infinitive; volume I PDF page 95.'),
        ('2.1.2','didicimus','dicimus','Print reads dicimus, not the HTML didicimus; volume I PDF page 95.'),
        ('2.22.2','LEKTON','λεκτόν','Restore the printed Greek word; volume I PDF page 113.'),
        ('1.41.1','per quan','per quam','Correct HTML typo against the alternate volume-I scan, PDF page 102.'),
        ('1.41.1','APO TOU ISTOREIN','ἀπὸ τοῦ ἱστορεῖν','Restore printed Greek; alternate volume-I scan, PDF page 102.'),
    ]
    corrections=[{'refs':['2.1.1','2.1.2'],'operation':'split-section','reason':'The HTML has an unbracketed 2, merging printed II.1.2 into II.1.1. The print on PDF page 95 distinguishes the two sections.'}]
    for ref,old,new,reason in fixes:
        if old not in records[ref]: raise ValueError((ref,old))
        records[ref]=records[ref].replace(old,new)
        corrections.append({'ref':ref,'old':old,'new':new,'reason':reason})
    specs=[
        ('rhetoric','What rhetoric is for',['2.1.1','2.1.2'],[95],'Complete chapter II.1','Rhetoric links correctness, expression, public affairs, and ethical purpose.'),
        ('rhetoric-learning','The art that slips away',['2.2.1','2.2.2'],[95],'Complete chapter II.2','A short history of the discipline leads to a recognizable experience of reading and forgetting.'),
        ('orator','What makes an orator',['2.3.1','2.3.2'],[95,96],'Complete chapter II.3','The five parts of rhetoric form a useful map for modern readers.'),
        ('persuasion','Persuasion, praise, and judgment',[f'2.4.{n}' for n in range(1,5)],[96],'Four complete sections, II.4.1-4; the remainder of chapter II.4 is not included','The three kinds of speech and the roles of hope and fear remain engaging without the longer sequence of quotations.'),
        ('dialectic','Learning how to argue',['2.22.1','2.22.2'],[113],'Complete chapter II.22','Logic as a method of inquiry and distinction between true and false.'),
        ('fist-palm','The closed fist and the open hand',['2.23.1','2.23.2'],[113,114],'Two complete sections, II.23.1-2; the transition to philosophy in II.23.3 is not included','A compact, memorable image connects reasoning, public speech, and audience.'),
        ('history','What an eyewitness can tell',['1.41.1','1.41.2'],[102],'Complete chapter I.41','Connects grammar with memory, history, and claims to eyewitness knowledge.'),
    ]
    selections=[]
    for ident,title,refs,pages,scope,reason in specs:
        alt=ident=='history'
        selections.append({'id':ident,'title':title,'refs':refs,'volume':'I',
                           'scan_file':'latin/raw/lindsay-1911-google-volume.pdf' if alt else 'latin/raw/lindsay-1911-volume-I.pdf',
                           'scan_url':'https://archive.org/details/isidorihispalen00lindgoog' if alt else 'https://archive.org/details/isidori01isiduoft',
                           'pdf_pages':pages,'scope':scope,'selection_reason':reason,
                           'scores':{'reader_interest':2,'self_contained':2,'representative':2},
                           'decision':'include','decision_date':'2026-11-01','editor':'lead Codex agent under user-approved scope',
                           'sections':[{'ref':ref,'latin':records[ref]} for ref in refs]})
    data={'schema_version':1,'batch':'002-trivium','base_edition':'Lindsay, Oxford, 1911',
          'status':'selected working Latin collated against printed pages',
          'source_hashes':hashes,'selections':selections}
    for filename,value in [('source.json',data),('source-corrections.json',corrections)]:
        (TARGET/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Frozen',sum(len(s['sections']) for s in selections),'sections in',len(selections),'selections')
    print('source SHA256',hashlib.sha256((TARGET/'source.json').read_bytes()).hexdigest())


if __name__=='__main__': main()
