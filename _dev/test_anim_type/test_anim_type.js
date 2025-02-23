console.log(Model[1][0][0].AnimType)
console.log(Model[1][0][0].AnimationType)
console.log('-----')
console.log(Model[1][0][0].Animation.AxisStart)
console.log(Model[1][0][0].Animation.AxisEnd)
console.log('-----')
console.log(Model[1][0][0].ToGlobal(Model[1][0][0].Animation.AxisStart))
console.log(Model[1][0][0].ToGlobal(Model[1][0][0].Animation.AxisEnd))

console.log('-----')

let test2 =  Model[1][0][0].Animation
for (let key in test2) {
   // console.log(`${key}: ${test2[key]}`);
}

console.log('-----')
console.log(Model[3].ToGlobal(Model[3].Animation.AxisStart))
console.log(Model[3].ToGlobal(Model[3].Animation.AxisEnd))

console.log('-----')
console.log(Model[3].AnimType)
console.log(Model[3].AnimationType)