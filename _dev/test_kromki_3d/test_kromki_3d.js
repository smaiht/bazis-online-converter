












let test = Model[1].Butts[0]
console.log(test)

for (let key in test) {
    console.log(`${key}: ${test[key]}`);
}


let myprofile = test.Profile;


console.log('---')

let newc = NewContour();
newc.Load('kromka16.frw');
console.log('---')





var newItem = AddPanel(444, 666);
newItem.SetDefaultTransform();
newItem.Thickness = 22;
newItem.TextureOrientation = 2;
newItem.MaterialName = "Материал не указан";
newItem.Name = "item.name";
newItem.ArtPos = 5;
newItem.Build();

var Butt = newItem.Butts.Add();
Butt.ElemIndex = 0;
Butt.ClipPanel = true;
Butt.Material = "Кромка XX";
Butt.Sign =  16;
Butt.Thickness = 2;
Butt.Profile = newc;
// Butt.Profile = myprofile;

newItem.Build();



   console.log('test\n\n\n')
let test2 = newItem.Butts[0]
console.log(test2)

// test.Profile = myprofile
//test.Build();

for (let key in test2) {
    console.log(`${key}: ${test2[key]}`);
}








for (let key in myprofile) {
    console.log(`${key}`);
}


// var newItem2 = AddPanel(444, 666);
// newItem2.SetDefaultTransform();
// newItem2.Thickness = 22;
// newItem2.TextureOrientation = 2;
// newItem2.MaterialName = "Материал не указан";
// newItem2.Name = "item.name";
// newItem2.ArtPos = 5;
// newItem2.Build();

// newItem2.Translate(-555, -555, -555);

// var Butt = newItem2.Butts.Add();
// Butt.ElemIndex = 0;
// Butt.ClipPanel = true;
// Butt.Material = "Кромка XX";
// Butt.Sign =  16;
// Butt.Thickness = 2;
// Butt.Profile = myprofile


// newItem2.Build();









console.log('---')

let newc = NewContour();
newc.Load('kromka16.frw');
console.log('---')





var newItem = Model[2]
var Butt = newItem.Butts.Add();
Butt.ElemIndex = 3;
Butt.ClipPanel = true;
Butt.Material = "Кромка XX";
Butt.Sign =  16;
Butt.Thickness = 2;
//Butt.Profile = newc;

newItem.Build();




















/////////////////////////////////////////

console.log('---')

let newc = NewContour();
newc.Load('kr16.frw');
// newc.Load('kromka16.frw');
console.log('---')





var newItem = Model[1]
var Butt = newItem.Butts.Add();
Butt.ElemIndex = 5;
Butt.ClipPanel = true;
Butt.Material = "Кромка XX";
Butt.Sign =  16;
Butt.Thickness = 2;
Butt.Profile = newc;

newItem.Build();





let test2 =  Model[1].Butts
test2.Remove(test2[0]);
newItem.Build();





Model[1].Butts.Clear()
Model[1].Build()





/////////////// FINAL: ///////////// 
Model[1].Butts.Clear()
Model[1].Build()

// system.sleep(333);

let newc = NewContour();
newc.Load('kr16.frw');
var newItem = Model[1]

for (let i=0; i <= 5; i++) {
    var Butt = newItem.Butts.Add();
    Butt.ElemIndex = i;
    Butt.ClipPanel = true;
    Butt.Material = "Кромка XX";
    Butt.Sign =  16;
    Butt.Thickness = 2;
    Butt.Profile = newc;

}
    
newItem.Build();