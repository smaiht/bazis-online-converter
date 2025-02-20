
let fs = require('fs');
// IMPORTANT: start by openning .b3d file on the desktop.
// idk why FS is not working when starting bazis and then selecting a model

let vertices = [];
let faces = [];
let totalVertices = 0;

let minX = Infinity, minY = Infinity, minZ = Infinity;
let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;

function exportObject(obj) {
    if (obj.TriListsCount) {
        // console.log('TriListsCount: ', obj.TriListsCount)

        for(let i = 0; i < obj.TriListsCount; i++) {
            let triPack = obj.TriLists[i];

            for(let j = 0; j < triPack.Count; j++) {
                let tri = triPack.Triangles[j];

                // Преобразуем вершины в глобальные координаты
                let v1 = obj.ToGlobal(tri.Vertex1);
                let v2 = obj.ToGlobal(tri.Vertex2);
                let v3 = obj.ToGlobal(tri.Vertex3);

                // Конвертируем в метры и сразу обновляем габариты
                const v1m = [v1.x/1000, v1.y/1000, v1.z/1000];
                const v2m = [v2.x/1000, v2.y/1000, v2.z/1000];
                const v3m = [v3.x/1000, v3.y/1000, v3.z/1000];

                // Обновляем габариты
                [v1m, v2m, v3m].forEach(v => {
                    minX = Math.min(minX, v[0]);
                    minY = Math.min(minY, v[1]);
                    minZ = Math.min(minZ, v[2]);
                    maxX = Math.max(maxX, v[0]);
                    maxY = Math.max(maxY, v[1]);
                    maxZ = Math.max(maxZ, v[2]);
                });

                // Сохраняем точки
                vertices.push(v1m, v2m, v3m);

                let baseIndex = totalVertices + 1;
                faces.push(`f ${baseIndex} ${baseIndex+1} ${baseIndex+2}`);
                totalVertices += 3;
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

// Создаем OBJ контент со смещенными вершинами
const objVertices = vertices.map(v =>
    `v ${v[0] - center.x} ${v[1] - center.y} ${v[2] - center.z}`
);

const meshName = `model_${10}`;
const realSize = {
    x: maxX - minX,
    y: maxY - minY,
    z: maxZ - minZ
};

fs.writeFileSync(`${meshName}.obj`, [...objVertices, ...faces].join('\n'));
