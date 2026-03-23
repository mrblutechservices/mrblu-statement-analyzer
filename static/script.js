let allData = []
let filteredData = []


// ---------------- UPLOAD ----------------

function upload(){

// CLEAR OLD DATA

allData = []
filteredData = []

document.getElementById("bank").innerText = ""
document.getElementById("holder").innerText = ""
document.getElementById("account").innerText = ""
document.getElementById("customer").innerText = ""
document.getElementById("branch").innerText = ""
document.getElementById("ifsc").innerText = ""
document.getElementById("micr").innerText = ""
document.getElementById("mobile").innerText = ""
document.getElementById("email").innerText = ""
document.getElementById("period").innerText = ""

renderTable([])

let file = document.getElementById("pdf").files[0]

if(!file){
alert("Please select a PDF file")
return
}

let loading = document.getElementById("loading")
if(loading) loading.style.display = "block"

let formData = new FormData()
formData.append("pdf", file)

let bank = document.getElementById("bank_select").value
formData.append("bank", bank)

fetch("/upload", {
method: "POST",
body: formData
})
.then(res => res.json())
.then(data => {

console.log("SERVER RESPONSE:", data)

if(loading) loading.style.display = "none"

if(data.error){
alert(data.error)
return
}

allData = data.data || data.transactions || []
filteredData = [...allData]

console.log("Transactions loaded:", allData.length)

if (allData.length === 0) {
alert("No transactions found in this PDF")
return
}


// ------- STATEMENT INFO -------

if(data.info){

document.getElementById("bank").innerText = data.info.bank || ""

document.getElementById("holder").innerText =
data.info["Account Holder"] || ""

document.getElementById("account").innerText =
data.info["Account Number"] || ""

document.getElementById("customer").innerText =
data.info["Customer ID"] || ""

document.getElementById("branch").innerText =
data.info["Branch"] || ""

document.getElementById("ifsc").innerText =
data.info["IFSC"] || ""

document.getElementById("micr").innerText =
data.info["MICR"] || ""

document.getElementById("mobile").innerText =
data.info["Mobile"] || ""

document.getElementById("email").innerText =
data.info["Email"] || ""

document.getElementById("period").innerText =
data.info["Period"] || ""

}


// ------- COLUMN LIST -------

populateColumns(Object.keys(allData[0] || {}))


// ------- PARTY LIST -------

let parties = [...new Set(
allData.map(x => x.Party || x.AI_Party || "Unknown")
)]

populateNames(parties)


// ------- RENDER TABLE -------

renderTable(allData)

})
.catch(err => {

console.log(err)

if(loading) loading.style.display = "none"

alert("Server error while uploading")

})

}



// ---------------- TABLE RENDER ----------------

function renderTable(data){

filteredData = [...data]

let table = document.getElementById("table")

if(!table){
console.error("Table not found")
return
}

let thead = table.querySelector("thead")
let tbody = table.querySelector("tbody")

if(!thead || !tbody){
console.error("Table structure incorrect")
return
}

thead.innerHTML = ""
tbody.innerHTML = ""

if(!data || data.length === 0){

tbody.innerHTML = "<tr><td colspan='20'>No Data Found</td></tr>"
return

}

let columns = [
"Sr_No",
"Date",
"Value_Date",
"Party",
"Description",
"Mode",
"Type",
"Cheque_No",
"Debit",
"Credit",
"Balance",
"Branch_Code"
]

// HEADER

let headRow = document.createElement("tr")

columns.forEach(col=>{

let th = document.createElement("th")
th.innerText = col
headRow.appendChild(th)

})

thead.appendChild(headRow)


// BODY

data.forEach(row=>{

let tr = document.createElement("tr")

columns.forEach(col=>{

let td = document.createElement("td")

let value = row[col]

if(value === null || value === undefined){
value = ""
}

td.innerText = value

tr.appendChild(td)

})

tbody.appendChild(tr)

})

}




// ---------------- FILTERS ----------------

function applyFilters(){

let name = document.getElementById("party").value

let type = document.getElementById("type").value

let result = [...allData]


// PARTY FILTER

if(name !== "all"){

result = result.filter(x =>

(x.Party && x.Party.includes(name)) ||

(x.AI_Party && x.AI_Party.includes(name))

)

}


// DEBIT FILTER

if(type === "debit"){

result = result.filter(x =>

parseFloat(String(x.Debit).replace(/,/g,'')) > 0

)

}


// CREDIT FILTER

if(type === "credit"){

result = result.filter(x =>

parseFloat(String(x.Credit).replace(/,/g,'')) > 0

)

}

renderTable(result)

}




// ---------------- EXPORT ----------------

function download(){

if(!filteredData || filteredData.length === 0){

alert("No data to export")
return

}

fetch("/export_excel",{

method:"POST",

headers:{"Content-Type":"application/json"},

body:JSON.stringify(filteredData)

})
.then(res=>res.blob())
.then(blob=>{

let a = document.createElement("a")

a.href = URL.createObjectURL(blob)

a.download = "statement.xlsx"

a.click()

})

}




// ---------------- PARTY DROPDOWN ----------------

function populateNames(names){

let select = document.getElementById("party")

if(!select) return

select.innerHTML = '<option value="all">All Parties</option>'

names.forEach(n=>{

let opt = document.createElement("option")

opt.value = n
opt.text = n

select.appendChild(opt)

})

}




// ---------------- COLUMN DROPDOWN ----------------

function populateColumns(cols){

let select = document.getElementById("column")

if(!select) return

select.innerHTML = ""

cols.forEach(c=>{

let option = document.createElement("option")

option.value = c
option.text = c

select.appendChild(option)

})

}
