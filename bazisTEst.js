// Action.LoadModel('results/model.b3d');
// system.sleep(500);

let fs = require('fs');




let materials = new Map();
let details2 = new Map();

// Функция для обработки объекта
function getMaterialGuid(materialName, component) {
    let materialGUID;
    
    if (!materials.has(materialName)) {
        // Если материал не найден, ищем подходящий и добавляем в Map
        materialGUID = findMaterial(materialName, sys_mats);
        materials.set(materialName, materialGUID);
        details2.set(materialName, [component.path + '/' + component.name]);
    } else {
        // Если материал уже есть, получаем его GUID и добавляем деталь в список
        materialGUID = materials.get(materialName);
        details2.get(materialName).push(component.path + '/' + component.name);
    }

    return materialGUID;
}




function quaternionToEuler(q) {
    const rad2deg = 180 / Math.PI;
    const {x, y, z, w} = q;
    let pitch, yaw, roll;

    // Тангаж (поворот вокруг X)
    const sinp = 2 * (w * x - y * z);
    if (Math.abs(sinp) >= 1) {
        // pitch = Math.copySign(Math.PI / 2, sinp);
        pitch = sinp >= 0 ? Math.PI / 2 : -Math.PI / 2;
    } else {
        pitch = Math.asin(sinp);
    }

    // Рыскание (поворот вокруг Y)
    const siny_cosp = 2 * (w * y + x * z);
    const cosy_cosp = 1 - 2 * (x * x + y * y);
    yaw = Math.atan2(siny_cosp, cosy_cosp);

    // Крен (поворот вокруг Z)
    const sinr_cosp = 2 * (w * z + x * y);
    const cosr_cosp = 1 - 2 * (z * z + x * x);
    roll = Math.atan2(sinr_cosp, cosr_cosp);

    pitch *= rad2deg;
    yaw *= rad2deg;
    roll *= rad2deg;

    // Нормализуем углы в диапазон [-180, 180]
    const normalizeAngle = angle => ((angle + 180) % 360) - 180;

    const result = {
        x: normalizeAngle(pitch),
        y: normalizeAngle(yaw),
        z: normalizeAngle(roll)
    };

    // console.log(result);
    return result;
}


function multiplyQuaternions(q1, q2) {
    return {
        w: q1.w * q2.w - q1.x * q2.x - q1.y * q2.y - q1.z * q2.z,
        x: q1.w * q2.x + q1.x * q2.w + q1.y * q2.z - q1.z * q2.y,
        y: q1.w * q2.y - q1.x * q2.z + q1.y * q2.w + q1.z * q2.x,
        z: q1.w * q2.z + q1.x * q2.y - q1.y * q2.x + q1.z * q2.w
    };
}

function newGuid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0,
            v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function createRotateInput(inputName, angle) {
    return {
        "guid": newGuid(),
        "verbose_ru": null,
        "name": inputName,
        "type": 1,
        "value": 0,
        "settings": {
            "min": angle.min,
            "max": angle.max,
            "minText": null,
            "maxText": null,
            "manipulator_start": null,
            "manipulator_end": null,
            "manipulator_handle": null,
            "tag": "anim",
            "is_interactive": true,
            "event": null,
            "show_in_preview": false,
            "show_in_consult": true,
            "display_external": false
        },
        "is_active": true,
        "is_hidden": false,
        "hint": null,
        "order": 0,
        "related": null
    }
}

function createTranslateInput(inputName, offset) {
    return {
        "guid": newGuid(),
        "verbose_ru": null,
        "name": inputName,
        "type": 1,
        "value": 0,
        "settings": {
            "min": offset.min,
            "max": offset.max,
            "minText": null,
            "maxText": null,
            "manipulator_start": null,
            "manipulator_end": null,
            "manipulator_handle": null,
            "tag": "anim",
            "is_interactive": true,
            "event": null,
            "show_in_preview": false,
            "show_in_consult": true,
            "display_external": false
        },
        "is_active": true,
        "is_hidden": false,
        "hint": null,
        "order": 0,
        "related": null
    }
}

function createNodeGetInput(inputName, order) {
    return {
        "guid": newGuid(),
        "name": "Получить вход",
        "color": "#7dff63",
        "position": {
        "x": 300,
        "y": order*100
        },
        "method": {
        "name": "GetInputValue",
        "arguments": [
            {
            "name": "input",
            "value": inputName,
            "type": 20
            }
        ],
        "result": {
            "name": null,
            "value": null,
            "type": 1
        }
        },
        "order": order
    }
}
        
function createNodeSetRotation(partPathName, summRotGuid, order) {
    return  {
        "guid": newGuid(),
        "name": "Задать поворот",
        "color": "#df6aff",
        "position": {
          "x": 1300,
          "y": (order*100) - 150
        },
        "method": {
          "name": "SetComponentRotation",
          "arguments": [
            {
              "name": "comp",
              "value": partPathName,
              "type": 6
            },
            {
              "name": "ax",
              "value": {
                "node_guid": summRotGuid,
                "pair_key":  "E"
              },
              "type": 2
            },
            {
              "name": "ay",
              "value": {
                "node_guid": summRotGuid,
                "pair_key":  "F"
              },
              "type": 2
            },
            {
              "name": "az",
              "value": {
                "node_guid": summRotGuid,
                "pair_key":  "G"
              },
              "type": 2
            }
          ],
          "result": {
            "name": null,
            "value": null,
            "type": 0
          }
        },
        "order": order
    }
}

function getScriptContent(axisStart, axisEnd, component) {
    return `
function quaternionMultiply(a, b) {
    return {
        w: a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z,
        x: a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
        y: a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
        z: a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w
    };
}

function quaternionToEuler(q) {
    const rad2deg = 180 / Math.PI;
    const {x, y, z, w} = q;
    let pitch, yaw, roll;

    // Тангаж (поворот вокруг X)
    const sinp = 2 * (w * x - y * z);
    if (Math.abs(sinp) >= 1) {
        // pitch = Math.copySign(Math.PI / 2, sinp);
        pitch = sinp >= 0 ? Math.PI / 2 : -Math.PI / 2;
    } else {
        pitch = Math.asin(sinp);
    }

    // Рыскание (поворот вокруг Y)
    const siny_cosp = 2 * (w * y + x * z);
    const cosy_cosp = 1 - 2 * (x * x + y * y);
    yaw = Math.atan2(siny_cosp, cosy_cosp);

    // Крен (поворот вокруг Z)
    const sinr_cosp = 2 * (w * z + x * y);
    const cosr_cosp = 1 - 2 * (z * z + x * x);
    roll = Math.atan2(sinr_cosp, cosr_cosp);

    pitch *= rad2deg;
    yaw *= rad2deg;
    roll *= rad2deg;

    // Нормализуем углы в диапазон [-180, 180]
    const normalizeAngle = angle => ((angle + 180) % 360) - 180;

    const result = {
        x: normalizeAngle(pitch),
        y: normalizeAngle(yaw),
        z: normalizeAngle(roll)
    };

    return result;
}

function rotatePointAroundAxis(point, axisStart, axisEnd, angle) {
    // Переводим угол в радианы
    let angleRad = angle * Math.PI / 180;

    // Вычисляем вектор оси вращения
    let axis = {
        x: axisEnd.x - axisStart.x,
        y: axisEnd.y - axisStart.y,
        z: axisEnd.z - axisStart.z
    };

    // Нормализуем вектор оси
    let axisLength = Math.sqrt(axis.x * axis.x + axis.y * axis.y + axis.z * axis.z);
    let unitAxis = {
        x: axis.x / axisLength,
        y: axis.y / axisLength,
        z: axis.z / axisLength
    };

    // Создаем кватернион вращения
    let sinHalfAngle = Math.sin(angleRad / 2);
    let rotationQuaternion = {
        w: Math.cos(angleRad / 2),
        x: unitAxis.x * sinHalfAngle,
        y: unitAxis.y * sinHalfAngle,
        z: unitAxis.z * sinHalfAngle
    };

    // Переносим точку относительно начала оси вращения
    let translatedPoint = {
        x: point.x - axisStart.x,
        y: point.y - axisStart.y,
        z: point.z - axisStart.z
    };

    // Создаем кватернион из точки
    let pointQuaternion = {w: 0, x: translatedPoint.x, y: translatedPoint.y, z: translatedPoint.z};

    // Выполняем вращение
    let rotatedQuaternion = quaternionMultiply(
        quaternionMultiply(rotationQuaternion, pointQuaternion),
        {w: rotationQuaternion.w, x: -rotationQuaternion.x, y: -rotationQuaternion.y, z: -rotationQuaternion.z}
    );



    let initialQuat = { x: ${component.rotation.x}, y: ${component.rotation.y}, z: ${component.rotation.z}, w: ${component.rotation.w} };
    const finalQuaternion = quaternionMultiply(rotationQuaternion, initialQuat);
    
    // Преобразуем результат в углы Эйлера
    const finalEulers = quaternionToEuler(finalQuaternion);


    // Возвращаем точку обратно
    return {
        x: rotatedQuaternion.x + axisStart.x,
        y: rotatedQuaternion.y + axisStart.y,
        z: rotatedQuaternion.z + axisStart.z,
        ax: finalEulers.x,
        ay: finalEulers.y,
        az: finalEulers.z,
    };
}



// Точки, определяющие ось вращения
let axisStart = { x: ${axisStart.x}, y:  ${axisStart.y}, z:  ${axisStart.z} };
let axisEnd = { x:  ${axisEnd.x}, y:  ${axisEnd.y}, z:  ${axisEnd.z} };


// Начальная позиция детали (точка центра детали)
let initialPoint = { x: ${component.position.x}, y: ${component.position.y}, z: ${component.position.z} };
// Начальное вращение
let initialRot = { x: ${component.eulers.x}, y: ${component.eulers.y}, z: ${component.eulers.z} };
let initialQuat = { x: ${component.rotation.x}, y: ${component.rotation.y}, z: ${component.rotation.z}, w: ${component.rotation.w} };

// Выполняем поворот
let newPosition = rotatePointAroundAxis(initialPoint, axisStart, axisEnd, A);

B =  newPosition.x;
C =  newPosition.y;
D =  newPosition.z;

E =  newPosition.ax;
F =  newPosition.ay;
G =  newPosition.az;

`;}

function createNodeSumm(inputGuid, order, axisStart, axisEnd, component) {
    return  {
        "guid": newGuid(),
        "name": "Сумматор",
        "color": "#ff5e5e",
        "position": {
            "x": 800,
            "y": order*100
        },
        "method": {
            "name": "SumRun",
            "arguments": [
                {
                    "name": "positive_variables",
                    "value": [
                        {
                            "type": 2,
                            "key": "A",
                            "value": {
                                "node_guid": inputGuid,
                                "pair_key": null
                            }
                        }
                    ],
                    "type": 18
                },
                {
                    "name": "negative_variables",
                    "value": [],
                    "type": 18
                },
                {
                    "name": "script",
                    "value": getScriptContent(axisStart, axisEnd, component),
                    "type": 19
                }
          ],
          "result": {
                "name": null,
                "value": [
                    {
                        "type": 0,
                        "key": "Σ",
                        "value": 0
                    },
                    {
                        "type": 0,
                        "key": "B",
                        "value": component.position.x
                    },
                    {
                        "type": 0,
                        "key": "C",
                        "value": component.position.y
                    },
                    {
                        "type": 0,
                        "key": "D",
                        "value": component.position.z
                    },
                    {
                        "type": 0,
                        "key": "E",
                        "value": component.eulers.x
                    },
                    {
                        "type": 0,
                        "key": "F",
                        "value": component.eulers.y
                    },
                    {
                        "type": 0,
                        "key": "G",
                        "value": component.eulers.z
                    }
                ],
                "type": 18
            }
        },
        "order": order
    }
}

function createNodeSummForTransition(inputGuid, order, axisStart, axisEnd, component) {
    return  {
        "guid": newGuid(),
        "name": "Сумматор",
        "color": "#ff5e5e",
        "position": {
            "x": 800,
            "y": order*100
        },
        "method": {
            "name": "SumRun",
            "arguments": [
                {
                    "name": "positive_variables",
                    "value": [
                        {
                            "type": 2,
                            "key": "A",
                            "value": {
                                "node_guid": inputGuid,
                                "pair_key": null
                            }
                        }
                    ],
                    "type": 18
                },
                {
                    "name": "negative_variables",
                    "value": [],
                    "type": 18
                },
                {
                    "name": "script",
                    "value": `

    // Точки, определяющие ось вращения
    let axisStart = { x:  ${axisStart.x}, y:  ${axisStart.y}, z:  ${axisStart.z} };
    let axisEnd = { x:  ${axisEnd.x}, y:  ${axisEnd.y}, z:  ${axisEnd.z} };

    let axisVector = {
        x: axisEnd.x - axisStart.x,
        y: axisEnd.y - axisStart.y,
        z: axisEnd.z - axisStart.z
    };

    let offset = {
        x: axisVector.x * A/100,
        y: axisVector.y * A/100,
        z: axisVector.z * A/100,
    };

    B = ${component.position.x} + offset.x;
    C = ${component.position.y} + offset.y;
    D = ${component.position.z} + offset.z;

                    `,
                    "type": 19
                }
          ],
          "result": {
                "name": null,
                "value": [
                {
                    "type": 0,
                    "key": "Σ",
                    "value": 0
                },
                {
                    "type": 0,
                    "key": "B",
                    "value": 2
                },
                {
                    "type": 0,
                    "key": "C",
                    "value": 3
                },
                {
                    "type": 0,
                    "key": "D",
                    "value": 4
                }
                ],
                "type": 18
            }
        },
        "order": order
    }
}

function createNodeSetDetailInfo(partName, partNamePath, summGuid, order) {
    return  {
        "guid": newGuid(),
        "name": "Задать параметр детали",
        "color": "#788cff",
        "position": {
            "x": 1600,
            "y": order*100
        },
        "method": {
            "name": "SetComponentsFields",
            "arguments": [
                {
                    "name": "components",
                    "value": [
                        {
                        "type": 0,
                        "key": partName,
                        "value": partNamePath
                        }
                    ],
                    "type": 18
                },
                {
                    "name": "fields",
                    "value": [
                        {
                            "type": 2,
                            "key": "position.x",
                            "value": {
                                "node_guid": summGuid,
                                "pair_key": "B"
                            }
                        },
                        {
                            "type": 2,
                            "key": "position.y",
                            "value": {
                                "node_guid": summGuid,
                                "pair_key": "C"
                            }
                        },
                        {
                            "type": 2,
                            "key": "position.z",
                            "value": {
                                "node_guid": summGuid,
                                "pair_key": "D"
                            }
                        }
                    ],
                    "type": 18
                }
            ],
            "result": {
                "name": null,
                "value": null,
                "type": 0
            }
        },
        "order": 3
    }
}

function getNewComponentPosition(obj) {
    var prop1 = obj.GabMax;
    var prop2 = obj.GabMin;

    var xx = (prop1.x + prop2.x) / 2;
    var yy = (prop1.y + prop2.y) / 2;
    var zz = (prop1.z + prop2.z) / 2;

    return {
        "x": -xx,
        "y": yy,
        "z": zz
    };
}

function getAnimationPosition(obj) {
    var prop1 = obj.GabMax;
    var prop2 = obj.GabMin;

    var centerX = (prop1.x + prop2.x) / 2;
    var centerY = (prop1.y + prop2.y) / 2;
    var centerZ = (prop1.z + prop2.z) / 2;

    let axisStartOld = obj.ToGlobal(obj.Animation.AxisStart)
    let axisEndOld = obj.ToGlobal(obj.Animation.AxisEnd)

    var axisStartDelta = {
        x: axisStartOld.x - centerX,
        y: axisStartOld.y - centerY,
        z: axisStartOld.z - centerZ
    };

    var axisEndDelta = {
        x: axisEndOld.x - centerX,
        y: axisEndOld.y - centerY,
        z: axisEndOld.z - centerZ
    };

    // Вычисляем новые координаты центра в новой системе
    var newCenterX = -centerX;
    var newCenterY = centerY;
    var newCenterZ = centerZ;

    // Вычисляем новые координаты axisStart и axisEnd
    let newAxisStart = {
        x: newCenterX - axisStartDelta.x,
        y: newCenterY + axisStartDelta.y,
        z: newCenterZ + axisStartDelta.z
    };

    let newAxisEnd = {
        x: newCenterX - axisEndDelta.x,
        y: newCenterY + axisEndDelta.y,
        z: newCenterZ + axisEndDelta.z
    }


    let angle = obj.Animation.DoorAngle
    let doorAngle = {
        min: 0,
        max: 0,
    }

    // Invert ??
    let finalAxisStart = newAxisStart
    let finalAxisEnd = newAxisEnd

    if (
        obj.AnimType == 2
        || obj.AnimType == 4
    ) {
        finalAxisStart = newAxisEnd
        finalAxisEnd = newAxisStart
        doorAngle.max += angle

    } else if (
        obj.AnimType == 3
        || obj.AnimType == 5
    ) {
        finalAxisStart = newAxisStart
        finalAxisEnd = newAxisEnd
        doorAngle.min -= angle
    }

    return {
        center: {
            x: newCenterX,
            y: newCenterY,
            z: newCenterZ
        },
        axisStart: finalAxisStart,
        axisEnd: finalAxisEnd,
        doorAngle: doorAngle,
    };
}

function createComponent(obj, index, parentRotation = null) {
    let component = {};

    component.position = getNewComponentPosition(obj)

    let localRotation = {
        x: obj.Rotation.ImagPart.x,
        y: -obj.Rotation.ImagPart.y,
        z: -obj.Rotation.ImagPart.z,
        w: obj.Rotation.RealPart
    };
    component.rotation = parentRotation 
        ? multiplyQuaternions(parentRotation, localRotation) 
        : localRotation;

    component.eulers = quaternionToEuler(component.rotation)
    
    component.size = {
        "x": obj.TextureOrientation == ftoVertical ? obj.GSize.x : obj.GSize.x,
        "y": obj.TextureOrientation == ftoVertical ? obj.GSize.y : obj.GSize.y,
        "z": obj.Thickness
    };

    component.color = null;
    component.ignore_bounds = true;
    component.bake = null;
    component.processings = [];
    component.is_active = true;
    component.max_texture_size = 512;
    component.build_order = index;
    component.order = index;
    component.user_data = null;
    component.positioning_points = [];
    component.name = obj.Name + index;
    component.path = "Детали";
    component.guid = newGuid();
    
    // Something to do with materials ... it's a mess
    let matIndex = colors.findIndex(el => el == obj.Material.MaterialName);
    if ( matIndex == -1) {
        colors.push(obj.Material.MaterialName);
        details.push([component.path+'/'+component.name]);
    } else {
        details[matIndex].push(component.path+'/'+component.name);
    };
    let materialGUID = getMaterialGuid(obj.Material.MaterialName, component);

    component.material = "s123mat://" + materialGUID
    let arrKromok = [0, 0, 0, 0];
    let arrKromokZ = [0, 0, 0, 0];

    for (let k = 0; k < obj.Butts.Count; k++) {
        arrKromok[obj.Butts.Butts[k].ElemIndex] = obj.Butts.Butts[k].Thickness == 0.4 ? 1 : 2;
        arrKromokZ[obj.Butts.Butts[k].ElemIndex] = obj.Butts.Butts[k].Thickness;
    };

    component.modifier = {
        "cut_angle1": 0.0,
        "cut_angle2": 0.0,
        "back_material": component.material,
        "edges": [{
            "type": arrKromok[3],
            "material": component.material,
            "size": {
                "x": component.size.z,
                "y": 1000.0,
                "z": arrKromokZ[3]
            }

        }, {
            "type": arrKromok[2],
            "material": component.material,
            "size": {
                "x": component.size.z,
                "y": 1000.0,
                "z": arrKromokZ[2]
            }

        }, {
            "type": arrKromok[1],
            "material": component.material,
            "size": {
                "x": component.size.z,
                "y": 1000.0,
                "z": arrKromokZ[1]
            }

        }, {
            "type": arrKromok[0],
            "material": component.material,
            "size": {
                "x": component.size.z,
                "y": 1000.0,
                "z": arrKromokZ[0]
            }

        }],

        "type": 9
    };

    component.full_path = component.path+'/'+component.name

    return component
}

let meshCache = new Map();

function getMeshCacheKey(obj) {
    let count = 0;
    
    // get vertices
    function countRecursive(item) {
        if (item.TriListsCount) {
            for(let i = 0; i < item.TriListsCount; i++) {
                count += item.TriLists[i].Count * 3;
            }
        }
        
        if (item.List) {
            for(let i = 0; i < item.Count; i++) {
                countRecursive(item.Objects[i]);
            }
        }
    }
    
    countRecursive(obj);

    // get orientation
    function formatNumber(num) {
        return (Math.abs(parseFloat(num.toFixed(3))) < 0.001) ? "0" : num.toFixed(3);
    }
    
    function getOrientationKey(obj) {
        const localDirs = [
            {x: 1, y: 0, z: 0},
            {x: 0, y: 1, z: 0},
            {x: 0, y: 0, z: 1}
        ];
    
        return localDirs.map(dir => {
            const global = obj.NToGlobal(dir);
            return `${formatNumber(global.x)}_${formatNumber(global.y)}_${formatNumber(global.z)}`;
        }).join('_');
    }

    const orientation = getOrientationKey(obj);

    return `${obj.Name}_${count}_${orientation}`;
}

function getOrCreateMeshInfo(item, index) {
    const cacheKey = getMeshCacheKey(item);
    
    if (meshCache.has(cacheKey)) {
        return meshCache.get(cacheKey);
    }

    let vertices = [];
    let faces = [];
    let totalVertices = 0;
    
    let minX = Infinity, minY = Infinity, minZ = Infinity;
    let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;
    
    function exportObject(obj) {
        if (obj.TriListsCount) {
    
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
    
    exportObject(item);

    // Обработка пустой модели
    if (vertices.length === 0) {
        const defaultSize = 0.0001;
        vertices = [
            [0, 0, 0],
            [defaultSize, 0, 0],
            [0, defaultSize, 0]
        ];
        faces = ['f 1 2 3'];
        minX = 0;
        minY = 0;
        minZ = 0;
        maxX = defaultSize;
        maxY = defaultSize;
        maxZ = defaultSize;
    }

    // Вычисляем центр
    const center = {
        x: (minX + maxX) / 2,
        y: (minY + maxY) / 2,
        z: (minZ + maxZ) / 2
    };

    // Создаем OBJ контент со смещенными вершинами
    const objVertices = vertices.map(v => 
        `v ${v[0] - center.x} ${v[1] - center.y} ${v[2] - center.z}`
    );

    const meshName = `model_${index}`;
    const realSize = {
        x: maxX - minX,
        y: maxY - minY,
        z: maxZ - minZ
    };
    
    fs.writeFileSync(`results/${meshName}.obj`, [...objVertices, ...faces].join('\n'));

    const modelObject = {
        name: meshName,
        size: realSize,
        min: { x: minX, y: minY, z: minZ },
        max: { x: maxX, y: maxY, z: maxZ }
    };

    meshCache.set(cacheKey, modelObject);

    return modelObject;
}

function createMeshComponent(obj, index, parentRotation = null) {
    const meshInfo = getOrCreateMeshInfo(obj, index)

    let component = {};
    component.position = getNewComponentPosition(obj)
    // component.position = {
    //     "x": 0,
    //     "y": 0,
    //     "z": 0
    // };
    // let localRotation = {
    //     x: obj.Rotation.ImagPart.x,
    //     y: -obj.Rotation.ImagPart.y,
    //     z: -obj.Rotation.ImagPart.z,
    //     w: obj.Rotation.RealPart
    // };
    // component.rotation = parentRotation 
    //     ? multiplyQuaternions(parentRotation, localRotation) 
    //     : localRotation;
    // component.eulers = quaternionToEuler(component.rotation)
    component.rotation = {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
        "w": 1.0
    },
    
    component.size = {
        "x": meshInfo.size.x*1000,
        "y": meshInfo.size.y*1000,
        "z": meshInfo.size.z*1000
    };

    component.color = null;
    component.ignore_bounds = true;
    component.bake = null;
    component.processings = [];
    component.is_active = true;
    component.max_texture_size = 512;
    component.build_order = index;
    component.order = index;
    component.user_data = null;
    component.positioning_points = [];
    component.name = obj.Name + index;
    component.path = "Детали";
    component.guid = newGuid();
    
    // Something to do with materials ...
    let materialName = obj.Material ? obj.Material.MaterialName : "default_material";
    let matIndex = colors.findIndex(el => el == materialName);
    if ( matIndex == -1) {
        colors.push(materialName);
        details.push([component.path+'/'+component.name]);
    } else {
        details[matIndex].push(component.path+'/'+component.name);
    };
    let materialGUID = getMaterialGuid(materialName, component);

    component.material = "s123mat://" + materialGUID

    component.modifier = {
        "mesh": `file://${meshInfo.name}.fbx`,
        "node_name": null,
        "use_scale": true,
        "apply_offset": false,
        "mesh_size": {
            "x": meshInfo.size.x,
            "y": meshInfo.size.y,
            "z": meshInfo.size.z
        },
        "type": 3
    };

    component.full_path = component.path+'/'+component.name

    return component
}



let usedInputNames = {}
function generateUniqueInputName(baseName, type) {
    let idx = 0;
    let inputName;
    do {
        inputName = `${baseName}${idx > 0 ? idx : ''} ${type}`;
        idx++;
    } while (usedInputNames[inputName]);

    usedInputNames[inputName] = true;
    return inputName;
}










let totalProcessed = 0;
const pauseInterval = 2;

function processLevel(
    item, 
    depth, 
    parentRotation = null, 

    currentAnimType = null, 
    initialPoint = null, 
    axisStart = null, 
    axisEnd = null, 

    inputName = null
) {
    totalProcessed++;

    // console.log(item.Name)

    if (totalProcessed % pauseInterval === 0) {
        system.sleep(50);
    }

    let currentRotation = parentRotation;

    // BLOCK
    if (item.toString() === '[object TFurnBlock]') {
        
        let localRotation = {
            x: item.Rotation.ImagPart.x,
            y: -item.Rotation.ImagPart.y,
            z: -item.Rotation.ImagPart.z,
            w: item.Rotation.RealPart
        };
        currentRotation = parentRotation 
            ? multiplyQuaternions(parentRotation, localRotation) 
            : localRotation;

        
        if (item.AnimType) {
            console.log(item.Name)
            console.log(item.AnimType)
            console.log()
        }


        if (!currentAnimType && item.AnimType && item.Count) { // set current animation if not yet (only works for level 1)
            // what to do with 1 and etc?
            // 1 - just a block
            // 9 - leg(wtf?)
            // 10 - handle
            // 11 - front panel

            if (item.AnimType >= 2 && item.AnimType <= 5) { // Rotate
                currentAnimType = item.AnimType

                const newPositions = getAnimationPosition(item)
                initialPoint = newPositions.center // this is doing nothing at all
                axisStart = newPositions.axisStart
                axisEnd = newPositions.axisEnd
                let doorAngle = newPositions.doorAngle
                
                // inputName = `${item.Name} Поворот`
                inputName = generateUniqueInputName(item.Name, "Поворот")
                const newInput = createRotateInput(inputName, doorAngle)
                // inputs.push(newInput)
                console.log('input ROT created!!!')

            } else if (item.AnimType >= 6 && item.AnimType <= 8) { // Translate (8 - Z; 6,7 - X)
                currentAnimType = item.AnimType

                const newPositions = getAnimationPosition(item)
                axisStart = newPositions.axisStart
                axisEnd = newPositions.axisEnd

                // // get axis: 
                // // GLOBAL ?
                // axisStart = item.Animation.AxisStart // temporary
                // axisEnd = item.Animation.AxisEnd // temporary

                let offset = {min: 0, max: 100}

                // inputName = `${item.Name} Смещение`
                inputName = generateUniqueInputName(item.Name, "Смещение")
                const newInput = createTranslateInput(inputName, offset)
                // inputs.push(newInput)
                console.log('input TR created!!!')
            }
        }
    }

    // EVERYTHING ELSE
    // } else if (
    //     item.toString() == '[object TFurnPanel]' || 
    //     item.toString() == '[object TFastener]' || 
    //     item.toString() == '[object TFurnAsm]' ||
    //     item.toString() == '[object TAsmKit]' ||
    //     item.toString() == '[object TImportedMesh]' ||
    //     item.toString() == '[object TObsoleteBentPanel]' ||
    //     item.toString() == '[object TRotationBody]' ||
    //     item.toString() == '[object TExtrusionBody]'
    // ) {
    else if (
        item.toString() != '[object TModel3D]' &&
        item.toString() != '[object TModelLimits]'
    ) {
        if (item.toString() == '[object TFurnPanel]') {
            // component = createComponent(item, totalProcessed, parentRotation);

        } else {
            // console.log(1)
            // console.log(item.toString())
            // component = createMeshComponent(item, totalProcessed, parentRotation);

        }

        // currentRotation = component.rotation;

        if (currentAnimType) { // if they are a part of the animation

            if (currentAnimType >= 2 && currentAnimType <= 5) { // Rotate

                console.log('rot!')
                

            } else if (currentAnimType >= 6 && currentAnimType <= 8) { // Translate

                console.log('tr!')
            }

        }


    }



    if (item.toString() === '[object TFurnBlock]' && item.Count) {
        for (let i = 0; i < item.Count; i++) {
            processLevel(item[i], depth + 1, currentRotation, 
                currentAnimType, initialPoint, axisStart, axisEnd, inputName);
        }
    }
}





for (let i = 0; i < Model.Count; i++) {

    if (Model[i].Visible) {

        // console.log(Model[i].toString())
        
        processLevel(Model[i], 1, null);

    };
};
