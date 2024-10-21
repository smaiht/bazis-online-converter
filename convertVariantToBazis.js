let fs = require('fs');

const content = fs.readFileSync('results/project.s123proj', 'utf8');
system.sleep(500);

Action.LoadModel('results/bazis-base-model.b3d');
system.sleep(500);

let project = JSON.parse(content);

for (var item of project.components) {

// for (let kk = 0; kk <= project.components.length; kk++) {
//     if (kk === project.components.length) {
//         system.sleep(500);

//         SetCamera(p3dLeft);
//         Action.DS.ViewAll();
//         system.sleep(500);

//         Action.SaveModel('results/bazis.b3d');
//         console.log("Модель сохранена");

//         break;
//     }

//     let item = project.components[kk];

    system.sleep(10);
    if (item.is_active) {

        var newItem = AddPanel(item.size.x, item.size.y);
        newItem.SetDefaultTransform();
        newItem.Thickness = item.size.z;
        newItem.TextureOrientation = ftoVertical; //2 == ftoVertical
        newItem.MaterialName = item.material_content ? item.material_content.name : "Материал не указан";
        newItem.Name = item.name;
        newItem.ArtPos = item.order;
        newItem.Build();

        newItem.Rotation = {
            ImagPart: {
                x: item.rotation.x,
                y: -item.rotation.y,
                z: -item.rotation.z
            },
            RealPart: item.rotation.w
        };

        var prop1 = newItem.GabMax;
        var prop2 = newItem.GabMin;

        var xx = (prop1.x + prop2.x) / 2;
        var yy = (prop1.y + prop2.y) / 2;
        var zz = (prop1.z + prop2.z) / 2;

        newItem.Translate(-xx, -yy, -zz);

        newItem.Translate(-item.position.x,
            item.position.y,
            item.position.z
        );

        if (item.modifier.type == 9) { // если это ЛДСП
            var Pan = newItem;
            var i = 3;
            item.modifier.edges.forEach(edge => {
                if (edge.type != 0) {
                    var Butt = Pan.Butts.Add(); // говорит о том что намерены установить кромку методо Butts и спомащью его свойст.
                    Butt.ElemIndex = i; // кромящаяся сторона
                    Butt.ClipPanel = true; // подрезка
                    Butt.Material = "Кромка " + ( (edge.material_content && edge.material_content.name) ? edge.material_content.name : "") + " \rXX"; // наименование кромки \r артикул
                    Butt.Sign = ( (edge.material_content && edge.material_content.name) ? edge.material_content.name : "") + " " + edge.size.z + "/" + item.size.z; // 16; // обозначение кромки
                    Butt.Thickness = (edge.size.z); // (2); // толщина кромки
                };

                i = i - 1;
            });
        };

        newItem.Build();
    };
};

fs.writeFileSync('results/flag-to-ctrl-s.json', JSON.stringify('ready', null, 2));