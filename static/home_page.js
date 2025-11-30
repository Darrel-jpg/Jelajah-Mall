// ==========================================
// 1. GLOBAL VARIABLES & CONFIGURATION
// ==========================================
const floorMap = document.getElementById("floorMap");
const dropdownLabel = document.getElementById("dropdownLabel");
const markerContainer = document.getElementById("marker-container");
const petaContainer = document.querySelector(".peta-container");

// State Management
let currentRouteCoords = []; 
let currentFloorKeyGlobal = ""; 
let globalRouteData = []; 

// KONFIGURASI KALIBRASI
const CONFIG = {
    BASIS_LEBAR: 1150, 
    BASIS_TINGGI: 610,
    MARKER_OFFSET_X: 5,  
    MARKER_OFFSET_Y: 20,
    ROUTE_OFFSET_X: 5,   
    ROUTE_OFFSET_Y: 0
};

// Setup Canvas Layer
const canvas = document.createElement("canvas");
canvas.style.pointerEvents = "none"; 
canvas.style.position = "absolute";
canvas.style.top = "0";
canvas.style.left = "0";
canvas.style.zIndex = "10"; 
petaContainer.appendChild(canvas);
const ctx = canvas.getContext("2d");


// ==========================================
// 2. HELPER FUNCTIONS (UTILITIES)
// ==========================================

function calculateScale() {
    const currentWidth = floorMap.offsetWidth || CONFIG.BASIS_LEBAR;
    const scale = currentWidth / CONFIG.BASIS_LEBAR;
    
    return {
        scaleX: scale,
        scaleY: scale 
    };
}

function clearMarkers() {
    markerContainer.innerHTML = "";
}

function clearRoute() {
    canvas.width = floorMap.offsetWidth;
    canvas.height = floorMap.offsetHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    currentRouteCoords = [];
}


// ==========================================
// 3. CORE VISUALIZATION LOGIC
// ==========================================

function drawMarkers(floorKey) {
    clearMarkers();
    currentFloorKeyGlobal = floorKey; 

    if (!markers[floorKey]) return;

    const { scaleX, scaleY } = calculateScale();

    markers[floorKey].forEach((marker) => {
        const markerEl = document.createElement("div");
        markerEl.classList.add("marker");

        const posX = (marker.x * scaleX) - CONFIG.MARKER_OFFSET_X;
        const posY = (marker.y * scaleY) - CONFIG.MARKER_OFFSET_Y;

        markerEl.style.left = `${posX - 10}px`; 
        markerEl.style.top = `${posY - 10}px`;  
        
        markerEl.style.backgroundImage = "url(/static/images/ikon-lokasi-20px.png)";
        markerEl.setAttribute("id", `marker-${marker.name.replace(/\s+/g, "-")}`);
        
        const tooltip = document.createElement("div");
        tooltip.classList.add("tooltip");
        tooltip.textContent = marker.name;

        markerEl.addEventListener("mouseenter", () => {
            tooltip.style.display = 'block'; 
            const mLeft = parseFloat(markerEl.style.left);
            const mTop = parseFloat(markerEl.style.top);
            
            requestAnimationFrame(() => {
                const tRect = tooltip.getBoundingClientRect();
                tooltip.style.left = `${mLeft + 10 - (tRect.width / 2)}px`;
                tooltip.style.top = `${mTop - tRect.height - 8}px`; 
                tooltip.style.opacity = "1";
            });
        });

        markerEl.addEventListener("mouseleave", () => {
            tooltip.style.display = 'none';
            tooltip.style.opacity = "0";
        });

        markerContainer.appendChild(markerEl);
        markerContainer.appendChild(tooltip);
    });
}

function drawRoute(coords) {
    currentRouteCoords = coords;

    canvas.width = floorMap.offsetWidth;
    canvas.height = floorMap.offsetHeight;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (!coords || coords.length === 0) return;

    const { scaleX, scaleY } = calculateScale();

    ctx.strokeStyle = "#2563eb"; 
    ctx.lineWidth = 5;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.shadowColor = "rgba(37, 99, 235, 0.5)";
    ctx.shadowBlur = 10;
    ctx.setLineDash([10, 10]);

    ctx.beginPath();

    coords.forEach((point, index) => {
        const x = (point.coord[0] * scaleX) - CONFIG.ROUTE_OFFSET_X;
        const y = (point.coord[1] * scaleY) - CONFIG.ROUTE_OFFSET_Y;

        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });

    ctx.stroke();
    ctx.setLineDash([]);
    ctx.shadowBlur = 0;
}

function drawRouteSmart() {
    if (!globalRouteData || globalRouteData.length === 0) return;

    const currentFloorNum = currentFloorKeyGlobal ? currentFloorKeyGlobal.replace("floor-", "") : "1";

    const filteredCoords = globalRouteData.filter(point => {
        const nodeInfo = node_coords[point.name];
        return String(nodeInfo.lantai) === String(currentFloorNum);
    });

    drawRoute(filteredCoords);
}


// ==========================================
// 4. EVENT LISTENERS & INITIALIZATION
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    
    if (Object.keys(markers).length > 0) {
        const firstFloor = Object.keys(markers)[0];
        const initMap = () => drawMarkers(firstFloor);
        
        if (floorMap.complete && floorMap.naturalWidth !== 0) {
            initMap();
        } else {
            floorMap.onload = initMap;
        }
    }
    
    setupFloorSelector();
    setupSearchFunctionality();
    setupRouteButtons();
    munculkanTooltipSidebar();
});

window.addEventListener("resize", () => {
    if (currentFloorKeyGlobal) {
        drawMarkers(currentFloorKeyGlobal);
    }
    if (globalRouteData.length > 0) {
        drawRouteSmart();
    } else if (currentRouteCoords.length > 0) {
        drawRoute(currentRouteCoords);
    }
});


// ==========================================
// 5. UI INTERACTION HANDLERS
// ==========================================

function setupFloorSelector() {
    const dropdownItems = document.querySelectorAll(".dropdown-item");
    
    dropdownItems.forEach((item) => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const floorKey = item.getAttribute("data-key");
            const imgSrc = item.getAttribute("data-image");
            const floorName = item.textContent.trim();

            dropdownLabel.textContent = floorName;
            
            floorMap.onload = () => {
                drawMarkers(floorKey);
                
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                drawRouteSmart(); 
            };
            floorMap.setAttribute("src", imgSrc);
        });
    });
}

function setupSearchFunctionality() {
    const searchBox = document.getElementById("searchBox");
    searchBox.addEventListener("keypress", (e) => {
        if (e.key === "Enter") performSearch(e.target.value, "listToko");
    });

    setupDropdownSearch("searchAwal", "lokasiAwal", "dropdown-button-awal", "dropdown-menu-awal");
    setupDropdownSearch("searchTujuan", "lokasiTujuan", "dropdown-button-tujuan", "dropdown-menu-tujuan");
}

function performSearch(query, listId, callback = null) {
    fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query }),
    })
    .then((res) => res.json())
    .then((data) => {
        const listContainer = document.getElementById(listId);
        listContainer.innerHTML = "";
        
        data.list_toko.forEach((toko) => {
            const li = document.createElement("li");
            
            if (listId === "listToko") {
                li.className = "nav-item";
                li.innerHTML = `<a href="#"><i class="fa-solid fa-location-dot"></i><span>${toko}</span></a>`;
            } else {
                li.innerHTML = `<a href="#" class="block px-4 py-2 hover:bg-blue-50 hover:text-blue-700 rounded-md">${toko}</a>`;
            }
            
            li.querySelector("a").addEventListener("click", (e) => {
                e.preventDefault();
                if (callback) callback(toko);
            });
            
            listContainer.appendChild(li);
        });
        
        if (listId === "listToko") munculkanTooltipSidebar();
    });
}

function setupDropdownSearch(inputId, listId, btnId, menuId) {
    const input = document.getElementById(inputId);
    const btn = document.getElementById(btnId);
    const menu = document.getElementById(menuId);
    const span = btn.querySelector("span");

    btn.addEventListener("click", (e) => {
        e.stopPropagation();
        document.querySelectorAll(".dropdown-menu").forEach(el => {
            if (el.id !== menuId) el.classList.add("hidden");
        });
        menu.classList.toggle("hidden");
    });

    window.addEventListener("click", () => menu.classList.add("hidden"));
    menu.addEventListener("click", (e) => e.stopPropagation());

    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            performSearch(e.target.value, listId, (selectedToko) => {
                span.textContent = selectedToko;
                menu.classList.add("hidden");
            });
        }
    });

    const initialLinks = document.querySelectorAll(`#${listId} a`);
    initialLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            span.textContent = link.textContent;
            menu.classList.add("hidden");
        });
    });
}

// --- Route & Sidebar Interaction ---

function munculkanTooltipSidebar() {
    const listItems = document.querySelectorAll("#listToko li");
    listItems.forEach((item) => {
        item.addEventListener("click", () => {
            const tokoName = item.querySelector("span").textContent.trim();
            focusOnToko(tokoName);
        });
    });
}

function focusOnToko(tokoName) {
    let targetFloor = null;
    
    for (const floor in markers) {
        const marker = markers[floor].find(m => m.name.toLowerCase() === tokoName.toLowerCase());
        if (marker) {
            targetFloor = floor;
            break;
        }
    }

    if (targetFloor) {
        const selectedFloor = floors.find(f => f.key === targetFloor);
        if (selectedFloor) {
            dropdownLabel.textContent = selectedFloor.name;
            const currentSrc = floorMap.getAttribute("src");
            
            const doHighlight = () => {
                highlightMarker(tokoName);
                clearRoute();
            };

            if (!currentSrc.includes(selectedFloor.image)) {
                floorMap.onload = () => {
                    drawMarkers(targetFloor);
                    doHighlight();
                };
                floorMap.setAttribute("src", selectedFloor.image);
            } else {
                doHighlight();
            }
        }
    }
}

function highlightMarker(tokoName) {
    const markerId = `marker-${tokoName.replace(/\s+/g, "-")}`;
    const markerEl = document.getElementById(markerId);
    if (markerEl) {
        markerEl.style.zIndex = "100";
        
        const eventEnter = new Event("mouseenter");
        markerEl.dispatchEvent(eventEnter);
        
        setTimeout(() => {
            markerEl.style.transform = "scale(1)";
            markerEl.style.zIndex = "30";
            markerEl.style.filter = "none";
            const eventLeave = new Event("mouseleave");
            markerEl.dispatchEvent(eventLeave);
        }, 2000);
    }
}

function setupRouteButtons() {
    const findRouteBtn = document.getElementById("cari-rute-btn");
    const spanAwal = document.querySelector("#dropdown-button-awal span");
    const spanTujuan = document.querySelector("#dropdown-button-tujuan span");

    findRouteBtn.addEventListener("click", () => {
        const start = spanAwal.textContent.trim();
        const goal = spanTujuan.textContent.trim();

        if (start.includes("Pilih") || goal.includes("Pilih")) {
            alert("Harap pilih Lokasi Awal dan Tujuan terlebih dahulu.");
            return;
        }

        const startNodeInfo = node_coords[start];
        const goalNodeInfo = node_coords[goal];

        if (!startNodeInfo || !goalNodeInfo) {
            alert("Data lokasi tidak ditemukan di sistem.");
            return;
        }

        const targetFloorNum = String(startNodeInfo.lantai).trim();
        const targetFloorKey = `floor-${targetFloorNum}`;
        const selectedFloor = floors.find((f) => f.key === targetFloorKey);

        const executeRouteFetch = () => {
            fetch(`/route?start=${encodeURIComponent(start)}&goal=${encodeURIComponent(goal)}`)
                .then(res => res.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                        return;
                    }
    
                    globalRouteData = data.coordinates; 
                    drawRouteSmart();                 
                })
                .catch(err => console.error("Route Error:", err));
        };

        if (selectedFloor && dropdownLabel.textContent !== selectedFloor.name) {
            dropdownLabel.textContent = selectedFloor.name;
            
            floorMap.onload = () => {
                drawMarkers(targetFloorKey);
                executeRouteFetch();
            };
            floorMap.setAttribute("src", selectedFloor.image);
        } else {
            executeRouteFetch();
        }
    });
}