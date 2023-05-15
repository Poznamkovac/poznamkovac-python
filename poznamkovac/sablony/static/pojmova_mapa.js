function vytvoritPojmovuMapu(DATA) {
    const pojmova_mapa_element = document.getElementById("pojmova_mapa");
    const sirkaZobrazenia = window.innerWidth;
    const jeSirokeZobrazenie = sirkaZobrazenia > 768;

    const bunky = new vis.DataSet(DATA.bunky);
    const spojenia = new vis.DataSet(DATA.spojenia);

    const dataSiete = {
        nodes: bunky,
        edges: spojenia
    };


    let jeZvyraznene = false;
    let vsetkyBunky = {};
    DATA.bunky.forEach((bunka) => vsetkyBunky[bunka.id] = {...bunka});

    const nastavenia = {
        interaction: {
            hover: true,
        },
        nodes: {
            shape: 'box',
            widthConstraint: {
                maximum: 200,
            },
            margin: 10,
            labelHighlightBold: false
        },
        edges: {
            smooth: {
                type: 'dynamic',
                roundness: 1.0
            },
            width: 0.15,
            arrows: {
                to: {
                    enabled: true
                }
            }
        },
        layout: {
            hierarchical: {
                enabled: true,
                direction: jeSirokeZobrazenie ? 'UD' : 'LR',
                sortMethod: 'directed',
                nodeSpacing: jeSirokeZobrazenie ? 220 : 100,
                levelSeparation: jeSirokeZobrazenie ? 100 : 250
            }
        },
        physics: false
    };


    function vykreslitMapu(siet) {
        pojmova_mapa = new vis.Network(pojmova_mapa_element, siet, nastavenia);

        pojmova_mapa.on("hoverNode", (parametre) => {
            zvyraznitOkolie(parametre);
            zobrazitTooltip(parametre.node);
        });

        pojmova_mapa.on("blurNode", () => {
            odstranitZvyraznenie();
            tippyInstancia.hide();
        });

        pojmova_mapa.on("click", (parametre) => {
            tippyInstancia.hide();

            if (parametre.nodes.length) {
                navigovatNaBunku(parametre.nodes[0]);
            }
        });
    };


    function zvyraznitOkolie(parametre) {
        function _pridatPriehladnost(hex_farba, priehladnost) {
            var _priehladnost = Math.round(Math.min(Math.max(priehladnost || 1, 0), 1) * 255);
    
            return hex_farba + _priehladnost.toString(16).toUpperCase();
        }

        if (jeZvyraznene) return;
        jeZvyraznene = true;

        const vybranaBunka = parametre.node; 
        const stupne = 2;

        let vsetkyZvyrazneneBunky = [];
    
        for (let bunkaId in vsetkyBunky) {
            vsetkyBunky[bunkaId].color = _pridatPriehladnost(vsetkyBunky[bunkaId].color, 0.25);
        }

        let pripojeneBunkyStupna = [vybranaBunka];
        vsetkyZvyrazneneBunky.push(vybranaBunka);

        for (let i = 0; i < stupne; i++) {
            let dalsiePripojeneBunky = [];
            pripojeneBunkyStupna.forEach(function (bunkaId) {
                pojmova_mapa.getConnectedNodes(bunkaId).forEach(function (pripojenaBunkaId) {
                    if (!pripojeneBunkyStupna.includes(pripojenaBunkaId)) {
                        dalsiePripojeneBunky.push(pripojenaBunkaId);
                    }
                });
            });

            pripojeneBunkyStupna = dalsiePripojeneBunky;
            vsetkyZvyrazneneBunky = vsetkyZvyrazneneBunky.concat(pripojeneBunkyStupna);
        };

        vsetkyZvyrazneneBunky.forEach(function (bunkaId) {
            vsetkyBunky[bunkaId].color = DATA.bunky.find(b => b.id == bunkaId).color;
        });

        bunky.update(Object.values(vsetkyBunky));
    }

    function odstranitZvyraznenie() {
        jeZvyraznene = false;

        for (let bunkaId in vsetkyBunky) {
            vsetkyBunky[bunkaId].color = DATA.bunky.find(b => b.id == bunkaId).color;
        }

        bunky.update(Object.values(vsetkyBunky));
    }


    let poslednaKliknutaBunkaId;
    let casPoslednehoKliknutiaNaBunku;

    function navigovatNaBunku(bunkaId) {
        function _navigovat() {
            window.location.hash = null;

            const titulokBunky = bunky.get(bunkaId).label;
            const urlHash = '#' + titulokBunky.toLowerCase().normalize("NFD").replace(/[^a-zA-Z0-9\s-]/g, "").replace(/\s+/g, "-").replace(/--+/g, "-");
            window.location.hash = urlHash;
        }

        if (window.navigator.maxTouchPoints > 0) {
            const aktualnyCas = new Date().getTime();

            if (poslednaKliknutaBunkaId === bunkaId && aktualnyCas - casPoslednehoKliknutiaNaBunku < 500) {
                _navigovat();
            }

            poslednaKliknutaBunkaId = bunkaId;
            casPoslednehoKliknutiaNaBunku = aktualnyCas;
        } else {
            _navigovat();
        }
    }      


    const tippyInstancia = tippy(document.createElement('div'), {
        allowHTML: true,
        arrow: false,
        animation: 'scale',
        duration: 150,
        zIndex: 9999,
        content: '',
    });

    function zobrazitTooltip(bunkaId) {
        const tooltip = DATA.tooltipy.find(t => t.id === bunkaId)
        const obsahTooltipu = tooltip !== undefined ? tooltip.content : null;
        if (obsahTooltipu === null) { return }

        tippyInstancia.setContent(`<div class="markdown-body" style="padding: 1rem 0.5rem; font-size: ${jeSirokeZobrazenie ? '14px' : '12px'}; background-color: transparent;">${obsahTooltipu}</div>`);

        tippyInstancia.setProps({
            triggerTarget: pojmova_mapa_element,
            maxWidth: '90vw',
            getReferenceClientRect: () => ({
                width: 0,
                height: 0,
                left: window.innerWidth / 2,
                right: window.innerWidth / 2,
                top: window.innerHeight - 10,
            }),
        });
    
        tippyInstancia.show();
    }

    vykreslitMapu(dataSiete);
}
