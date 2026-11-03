import { NodeIO } from '@gltf-transform/core';
import { simplifyPrimitive, weldPrimitive, joinPrimitives, prune } from '@gltf-transform/functions';
import { MeshoptSimplifier } from 'meshoptimizer';
await MeshoptSimplifier.ready;
const io = new NodeIO();
const doc = await io.read(process.argv[2]);
const target = Number(process.argv[4] || 4000);
const rollerTarget = Number(process.argv[5] || 600);
let before = 0, after = 0;
const done = new Set();
const tcount = p => { const i = p.getIndices(); return (i ? i.getCount() : p.getAttribute('POSITION').getCount()) / 3; };
for (const node of doc.getRoot().listNodes()) {
  const mesh = node.getMesh(); if (!mesh || done.has(mesh)) continue; done.add(mesh);
  const isRoller = /Roller__Roller/.test(node.getName());
  // join primitives that share a material so faces can be simplified together
  const byMat = new Map();
  for (const p of mesh.listPrimitives()) { const k = p.getMaterial(); if (!byMat.has(k)) byMat.set(k, []); byMat.get(k).push(p); }
  for (const [mat, prims] of byMat) {
    prims.forEach(p => { before += tcount(p); if (!p.getAttribute('TEXCOORD_0')) return; p.setAttribute('TEXCOORD_0', null); });
    let p = prims[0];
    if (prims.length > 1) {
      const sem = new Set(prims[0].listSemantics());
      const ok = prims.every(q => q.listSemantics().length === sem.size && q.listSemantics().every(s => sem.has(s)) && !!q.getIndices() === !!prims[0].getIndices());
      if (ok) { p = joinPrimitives(prims); p.setMaterial(mat); prims.forEach(q => { mesh.removePrimitive(q); }); mesh.addPrimitive(p); }
    }
    const t = tcount(p); const goal = isRoller ? rollerTarget : target;
    if (t > goal) {
      weldPrimitive(p, { tolerance: 0.0001 });
      simplifyPrimitive(p, { simplifier: MeshoptSimplifier, ratio: goal / t, error: isRoller ? 0.03 : 0.006 });
    }
  }
  mesh.listPrimitives().forEach(p => after += tcount(p));
}
await doc.transform(prune());
console.log('unique tris before', Math.round(before), 'after', Math.round(after));
await io.write(process.argv[3], doc);
