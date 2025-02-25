let fs = require('fs');

// Массивы для панели
let panelVertices = [];
let panelFaces = [];
let panelTotalVertices = 0;

// Массивы для кромок 
let buttVertices = [];
let buttFaces = []; 
let buttTotalVertices = 0;

let minX = Infinity, minY = Infinity, minZ = Infinity;
let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;

function exportObject(obj) {
   if (obj.TriListsCount) {
       for(let i = 0; i < obj.TriListsCount; i++) {
           let triPack = obj.TriLists[i];
           
           // Проверяем тип поверхности
           let isPanelSurface = triPack.toString() == "[object TFurnPanelSide]" || 
                               triPack.toString() == "[object TFurnPanelFace]";

           for(let j = 0; j < triPack.Count; j++) {
               let tri = triPack.Triangles[j];
               let v1 = obj.ToGlobal(tri.Vertex1);
               let v2 = obj.ToGlobal(tri.Vertex2);
               let v3 = obj.ToGlobal(tri.Vertex3);

               const v1m = [v1.x/1000, v1.y/1000, v1.z/1000];
               const v2m = [v2.x/1000, v2.y/1000, v2.z/1000];
               const v3m = [v3.x/1000, v3.y/1000, v3.z/1000];

               [v1m, v2m, v3m].forEach(v => {
                   minX = Math.min(minX, v[0]);
                   minY = Math.min(minY, v[1]);
                   minZ = Math.min(minZ, v[2]);
                   maxX = Math.max(maxX, v[0]);
                   maxY = Math.max(maxY, v[1]); 
                   maxZ = Math.max(maxZ, v[2]);
               });

               if (isPanelSurface) {
                   // Сохраняем в массивы панели
                   panelVertices.push(v1m, v2m, v3m);
                   let baseIndex = panelTotalVertices + 1;
                   panelFaces.push(`f ${baseIndex} ${baseIndex+1} ${baseIndex+2}`);
                   panelTotalVertices += 3;
               } else {
                   // Сохраняем в массивы кромок
                   buttVertices.push(v1m, v2m, v3m);
                   let baseIndex = buttTotalVertices + 1;
                   buttFaces.push(`f ${baseIndex} ${baseIndex+1} ${baseIndex+2}`);
                   buttTotalVertices += 3;
               }
           }
       }
   }

   if (obj.List) {
       for(let i = 0; i < obj.Count; i++) {
           exportObject(obj.Objects[i]);
           system.sleep(1);
       }
   }
}

exportObject(Model[1]);

const center = {
   x: (minX + maxX) / 2,
   y: (minY + maxY) / 2,
   z: (minZ + maxZ) / 2
};

// Экспорт панели
const panelObjVertices = panelVertices.map(v =>
   `v ${v[0] - center.x} ${v[1] - center.y} ${v[2] - center.z}`
);
fs.writeFileSync(`panel.obj`, [...panelObjVertices, ...panelFaces].join('\n'));

// Экспорт кромок
const buttObjVertices = buttVertices.map(v => 
   `v ${v[0] - center.x} ${v[1] - center.y} ${v[2] - center.z}`
);
fs.writeFileSync(`butts.obj`, [...buttObjVertices, ...buttFaces].join('\n'));