/**
 * Fix pour le téléchargement des graphiques Plotly
 * Ajoute un bouton de téléchargement personnalisé si le bouton natif échoue
 */

(function() {
    'use strict';

    // Configuration pour le téléchargement d'images
    const downloadConfig = {
        format: 'png',
        width: 1920,
        height: 1080,
        scale: 2
    };

    /**
     * Télécharge un graphique Plotly en utilisant l'API native
     */
    function downloadPlotlyChart(gd, filename = 'graphique') {
        // Nettoyer le nom de fichier
        filename = filename.replace(/\s+/g, '_').toLowerCase();
        
        // Essayer d'abord avec Plotly.downloadImage (méthode recommandée)
        if (typeof Plotly !== 'undefined' && Plotly.downloadImage) {
            Plotly.downloadImage(gd, {
                format: downloadConfig.format,
                width: downloadConfig.width,
                height: downloadConfig.height,
                filename: filename
            }).then(() => {
                console.log('✅ Téléchargement réussi via Plotly.downloadImage');
            }).catch((error) => {
                console.error('❌ Erreur Plotly.downloadImage:', error);
                // Fallback vers toImage + download manuel
                downloadViaToImage(gd, filename);
            });
        } else {
            // Fallback si downloadImage n'existe pas
            downloadViaToImage(gd, filename);
        }
    }

    /**
     * Méthode alternative utilisant Plotly.toImage
     */
    function downloadViaToImage(gd, filename) {
        if (typeof Plotly !== 'undefined' && Plotly.toImage) {
            Plotly.toImage(gd, {
                format: downloadConfig.format,
                width: downloadConfig.width,
                height: downloadConfig.height,
                scale: downloadConfig.scale
            }).then((dataUrl) => {
                // Créer un lien de téléchargement
                const link = document.createElement('a');
                link.href = dataUrl;
                link.download = `${filename}.${downloadConfig.format}`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                console.log('✅ Téléchargement réussi via Plotly.toImage');
            }).catch((error) => {
                console.error('❌ Erreur Plotly.toImage:', error);
                // Dernier recours : utiliser html2canvas
                downloadViaHtml2Canvas(gd, filename);
            });
        } else {
            downloadViaHtml2Canvas(gd, filename);
        }
    }

    /**
     * Dernier recours : utiliser html2canvas (nécessite la bibliothèque)
     */
    function downloadViaHtml2Canvas(gd, filename) {
        if (typeof html2canvas !== 'undefined') {
            html2canvas(gd).then((canvas) => {
                canvas.toBlob((blob) => {
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = `${filename}.png`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                    console.log('✅ Téléchargement réussi via html2canvas');
                });
            }).catch((error) => {
                console.error('❌ Erreur html2canvas:', error);
                alert('Impossible de télécharger le graphique. Essayez un autre navigateur ou faites une capture d\'écran.');
            });
        } else {
            // Si aucune méthode ne fonctionne
            console.error('❌ Aucune méthode de téléchargement disponible');
            alert('Téléchargement non disponible. Veuillez faire une capture d\'écran (Windows + Maj + S).');
        }
    }

    /**
     * Ajoute un bouton de téléchargement personnalisé à un conteneur
     */
    function addCustomDownloadButton(containerId, filename) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Vérifier si le bouton existe déjà
        if (container.querySelector('.custom-download-btn')) return;

        // Créer le bouton
        const button = document.createElement('button');
        button.className = 'custom-download-btn';
        button.innerHTML = '<i class="fas fa-download"></i> Télécharger';
        button.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1000;
            padding: 8px 16px;
            background: #6366f1;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
            transition: all 0.2s ease;
        `;

        button.addEventListener('mouseenter', () => {
            button.style.background = '#4f46e5';
            button.style.transform = 'translateY(-2px)';
            button.style.boxShadow = '0 4px 12px rgba(99, 102, 241, 0.4)';
        });

        button.addEventListener('mouseleave', () => {
            button.style.background = '#6366f1';
            button.style.transform = 'translateY(0)';
            button.style.boxShadow = '0 2px 8px rgba(99, 102, 241, 0.3)';
        });

        button.addEventListener('click', () => {
            const gd = container.querySelector('.js-plotly-plot, .plotly');
            if (gd) {
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Téléchargement...';
                button.disabled = true;
                
                setTimeout(() => {
                    downloadPlotlyChart(gd, filename);
                    button.innerHTML = '<i class="fas fa-download"></i> Télécharger';
                    button.disabled = false;
                }, 100);
            }
        });

        // Positionner le conteneur en relatif si nécessaire
        if (getComputedStyle(container).position === 'static') {
            container.style.position = 'relative';
        }

        container.appendChild(button);
    }

    /**
     * Configuration Plotly optimisée pour le téléchargement
     */
    window.getPlotlyConfigWithDownload = function(filename = 'graphique') {
        return {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToAdd: [{
                name: 'Télécharger PNG haute qualité',
                icon: {
                    width: 857.1,
                    height: 1000,
                    path: 'm214-7h429v214h-429v-214z m500 0h72v500q0 8-6 21t-11 20l-157 156q-5 6-19 12t-22 5v-232q0-22-15-38t-38-16h-322q-22 0-37 16t-16 38v232h-72v-714h72v232q0 22 16 38t37 16h465q22 0 38-16t15-38v-232z',
                    transform: 'matrix(1 0 0 -1 0 850)'
                },
                click: function(gd) {
                    downloadPlotlyChart(gd, filename);
                }
            }],
            toImageButtonOptions: {
                format: 'png',
                filename: filename,
                height: 1080,
                width: 1920,
                scale: 2
            },
            modeBarButtonsToRemove: [],
            staticPlot: false,
            plotGlPixelRatio: 2
        };
    };

    /**
     * Ajoute automatiquement des boutons de téléchargement à tous les graphiques
     */
    window.enableCustomPlotlyDownloads = function() {
        // Attendre que les graphiques soient rendus
        setTimeout(() => {
            const charts = [
                { id: 'mccabe-chart', name: 'mccabe_thiele' },
                { id: 'concentration-chart', name: 'evolution_concentration' },
                { id: 'column-chart', name: 'schema_colonne' },
                { id: 'mccabe2d', name: 'mccabe_2d' },
                { id: 'surface3d', name: 'surface_3d' }
            ];

            charts.forEach(chart => {
                if (document.getElementById(chart.id)) {
                    addCustomDownloadButton(chart.id, chart.name);
                }
            });
        }, 1000);
    };

    // Exposer les fonctions globalement
    window.downloadPlotlyChart = downloadPlotlyChart;
    window.addCustomDownloadButton = addCustomDownloadButton;

    console.log('✅ Plotly Download Fix chargé');
})();
