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

// KONFIGURASI KALIBRASI (Sesuai data terakhir Mas Adam)
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
canvas.style.zIndex = "10"; // Di atas peta, di bawah marker
petaContainer.appendChild(canvas);
const ctx = canvas.getContext("2d");


// ==========================================
// 2. HELPER FUNCTIONS (UTILITIES)
// ==========================================

// Fungsi sentral untuk menghitung skala saat ini
function calculateScale() {
    // Fallback ke BASIS jika gambar belum load sempurna
    const currentWidth = floorMap.offsetWidth || CONFIG.BASIS_LEBAR;
    
    // Hitung rasio
    const scale = currentWidth / CONFIG.BASIS_LEBAR;
    
    return {
        scaleX: scale,
        scaleY: scale // Lock Aspect Ratio (agar tidak gepeng)
    };
}

function clearMarkers() {
    markerContainer.innerHTML = "";
}

function clearRoute() {
    // Sesuaikan ukuran canvas dengan gambar saat menghapus
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

        // Rumus Transformasi Koordinat
        const posX = (marker.x * scaleX) - CONFIG.MARKER_OFFSET_X;
        const posY = (marker.y * scaleY) - CONFIG.MARKER_OFFSET_Y;

        markerEl.style.left = `${posX - 10}px`; // -10 untuk centering (half width)
        markerEl.style.top = `${posY - 10}px`;  // -10 untuk centering (half height)
        
        // Asset & ID
        markerEl.style.backgroundImage = "url(/static/images/ikon-lokasi-20px.png)";
        markerEl.setAttribute("id", `marker-${marker.name.replace(/\s+/g, "-")}`);
        
        // --- Tooltip Logic ---
        const tooltip = document.createElement("div");
        tooltip.classList.add("tooltip");
        tooltip.textContent = marker.name;

        // Hover Effect
        markerEl.addEventListener("mouseenter", () => {
            tooltip.style.display = 'block'; 
            // Kalkulasi posisi tooltip dinamis
            const mLeft = parseFloat(markerEl.style.left);
            const mTop = parseFloat(markerEl.style.top);
            
            // Render sebentar untuk dapat width
            requestAnimationFrame(() => {
                const tRect = tooltip.getBoundingClientRect();
                tooltip.style.left = `${mLeft + 10 - (tRect.width / 2)}px`;
                tooltip.style.top = `${mTop - tRect.height - 8}px`; // 8px gap
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

    // Pastikan resolusi canvas tajam sesuai ukuran gambar
    canvas.width = floorMap.offsetWidth;
    canvas.height = floorMap.offsetHeight;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (!coords || coords.length === 0) return;

    const { scaleX, scaleY } = calculateScale();

    // Style Garis
    ctx.strokeStyle = "#2563eb"; // Royal Blue
    ctx.lineWidth = 5;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.shadowColor = "rgba(37, 99, 235, 0.5)";
    ctx.shadowBlur = 10;
    
    // Animasi Garis Putus-putus (Optional Style)
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
    // Reset setting canvas
    ctx.setLineDash([]);
    ctx.shadowBlur = 0;
}


// ==========================================
// 4. EVENT LISTENERS & INITIALIZATION
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    
    // --- Initial Load ---
    if (Object.keys(markers).length > 0) {
        const firstFloor = Object.keys(markers)[0];
        const initMap = () => drawMarkers(firstFloor);
        
        if (floorMap.complete && floorMap.naturalWidth !== 0) {
            initMap();
        } else {
            floorMap.onload = initMap;
        }
    }
    
    // Setup Interaction Listeners
    setupFloorSelector();
    setupSearchFunctionality();
    setupRouteButtons();
    munculkanTooltipSidebar();
});

// Event: Window Resize (Responsiveness)
window.addEventListener("resize", () => {
    // Redraw everything on resize to keep coordinates accurate
    if (currentFloorKeyGlobal) {
        drawMarkers(currentFloorKeyGlobal);
    }
    if (currentRouteCoords.length > 0) {
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
            
            // Ganti Source Gambar
            floorMap.onload = () => {
                drawMarkers(floorKey);
                clearRoute(); 
            };
            floorMap.setAttribute("src", imgSrc);
        });
    });
}

function setupSearchFunctionality() {
    // Sidebar Search
    const searchBox = document.getElementById("searchBox");
    searchBox.addEventListener("keypress", (e) => {
        if (e.key === "Enter") performSearch(e.target.value, "listToko");
    });

    // Dropdown Search (Start & Goal)
    setupDropdownSearch("searchAwal", "lokasiAwal", "dropdown-button-awal", "dropdown-menu-awal");
    setupDropdownSearch("searchTujuan", "lokasiTujuan", "dropdown-button-tujuan", "dropdown-menu-tujuan");
}

// Logic Pencarian Generik
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
            
            // Styling berbeda tergantung list mana (Sidebar vs Dropdown)
            if (listId === "listToko") {
                li.className = "nav-item";
                li.innerHTML = `<a href="#"><i class="fa-solid fa-location-dot"></i><span>${toko}</span></a>`;
            } else {
                li.innerHTML = `<a href="#" class="block px-4 py-2 hover:bg-blue-50 hover:text-blue-700 rounded-md">${toko}</a>`;
            }
            
            // Add click listener
            li.querySelector("a").addEventListener("click", (e) => {
                e.preventDefault();
                if (callback) callback(toko);
            });
            
            listContainer.appendChild(li);
        });
        
        // Re-attach sidebar tooltip listeners if main list updated
        if (listId === "listToko") munculkanTooltipSidebar();
    });
}

function setupDropdownSearch(inputId, listId, btnId, menuId) {
    const input = document.getElementById(inputId);
    const btn = document.getElementById(btnId);
    const menu = document.getElementById(menuId);
    const span = btn.querySelector("span");

    // Toggle Menu
    btn.addEventListener("click", (e) => {
        e.stopPropagation();
        // Tutup menu lain
        document.querySelectorAll(".dropdown-menu").forEach(el => {
            if (el.id !== menuId) el.classList.add("hidden");
        });
        menu.classList.toggle("hidden");
    });

    // Close on outside click
    window.addEventListener("click", () => menu.classList.add("hidden"));
    menu.addEventListener("click", (e) => e.stopPropagation());

    // Search Enter Key
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            performSearch(e.target.value, listId, (selectedToko) => {
                span.textContent = selectedToko;
                menu.classList.add("hidden");
            });
        }
    });

    // Initial List Click
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
    
    // Cari lantai toko
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
        // Efek visual highlight
        // markerEl.style.transform = "scale(2.5)";
        markerEl.style.zIndex = "100";
        // markerEl.style.filter = "hue-rotate(90deg)"; // Ubah warna dikit
        
        // Trigger tooltip manual
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

        // Validasi
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

        if (String(startNodeInfo.lantai) !== String(goalNodeInfo.lantai)) {
            alert("Mohon maaf, rute antar lantai belum tersedia saat ini.");
            return;
        }

        // Logic Rute
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
                    drawRoute(data.coordinates);
                })
                .catch(err => console.error("Route Error:", err));
        };

        // Ganti lantai jika perlu
        if (selectedFloor && dropdownLabel.textContent !== selectedFloor.name) {
            dropdownLabel.textContent = selectedFloor.name;
            floorMap.setAttribute("src", selectedFloor.image);
            floorMap.onload = () => {
                drawMarkers(targetFloorKey);
                executeRouteFetch();
            };
        } else {
            executeRouteFetch();
        }
    });
}