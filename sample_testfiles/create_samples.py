import os,random
os.makedirs('sample_testfiles',exist_ok=True)
for i in range(10): open(f'sample_testfiles/normal_{i}.txt','w').write('This is normal file\n')
for i in range(10): open(f'sample_testfiles/file_{i}.bin','wb').write(os.urandom(1024*random.randint(1,50)))
open('sample_testfiles/important.docx.encrypted','w').write('simulated encrypted')
open('sample_testfiles/ransom_note.txt','w').write('This is harmless demo text')
print('Samples created in sample_testfiles')
