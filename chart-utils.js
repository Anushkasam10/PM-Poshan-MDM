// Shared configurations and theme utilities for ApexCharts
const ChartUtils = (() => {
    // Custom premium color palettes
    const PALETTES = {
        primary: ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#0ea5e9', '#8b5cf6', '#ec4899'],
        cool: ['#0ea5e9', '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e'],
        warm: ['#f59e0b', '#ff7849', '#ff5252', '#f43f5e', '#ec4899'],
        forest: ['#10b981', '#059669', '#047857', '#065f46', '#064e3b']
    };

    const getThemeColors = () => {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        return {
            mode: isDark ? 'dark' : 'light',
            text: isDark ? '#9ca3af' : '#64748b',
            border: isDark ? '#1f2937' : '#e2e8f0',
            grid: isDark ? '#1f2937' : '#f1f5f9',
            tooltipBg: isDark ? '#111827' : '#ffffff'
        };
    };

    const getDefaultOptions = (type = 'line') => {
        const theme = getThemeColors();
        
        return {
            chart: {
                type: type,
                fontFamily: 'Inter, sans-serif',
                foreColor: theme.text,
                toolbar: {
                    show: true,
                    tools: {
                        download: true,
                        selection: false,
                        zoom: false,
                        zoomin: false,
                        zoomout: false,
                        pan: false,
                        reset: false
                    }
                },
                background: 'transparent'
            },
            colors: PALETTES.primary,
            stroke: {
                width: type === 'line' || type === 'area' ? 3 : 0,
                curve: 'smooth'
            },
            grid: {
                borderColor: theme.grid,
                strokeDashArray: 4,
                padding: {
                    right: 20,
                    left: 20,
                    bottom: 0
                }
            },
            theme: {
                mode: theme.mode
            },
            tooltip: {
                theme: theme.mode,
                style: {
                    fontSize: '12px',
                    fontFamily: 'Inter, sans-serif'
                },
                y: {
                    formatter: function(val) {
                        return val.toLocaleString();
                    }
                }
            },
            xaxis: {
                labels: {
                    style: {
                        colors: theme.text,
                        fontSize: '12px'
                    }
                },
                axisBorder: {
                    show: false
                },
                axisTicks: {
                    show: false
                }
            },
            yaxis: {
                labels: {
                    style: {
                        colors: theme.text,
                        fontSize: '12px'
                    },
                    formatter: function(val) {
                        if (val >= 10000000) return (val / 10000000).toFixed(1) + ' Cr';
                        if (val >= 100000) return (val / 100000).toFixed(1) + ' L';
                        if (val >= 1000) return (val / 1000).toFixed(1) + ' K';
                        return val;
                    }
                }
            },
            legend: {
                position: 'top',
                horizontalAlign: 'right',
                fontFamily: 'Inter, sans-serif',
                fontSize: '12px',
                markers: {
                    radius: 12
                }
            }
        };
    };

    // Deep merge helper
    const mergeObjects = (target, source) => {
        const output = Object.assign({}, target);
        if (isObject(target) && isObject(source)) {
            Object.keys(source).forEach(key => {
                if (isObject(source[key])) {
                    if (!(key in target))
                        Object.assign(output, { [key]: source[key] });
                    else
                        output[key] = mergeObjects(target[key], source[key]);
                } else {
                    Object.assign(output, { [key]: source[key] });
                }
            });
        }
        return output;
    };

    const isObject = (item) => {
        return (item && typeof item === 'object' && !Array.isArray(item));
    };

    // Watch for theme changes and update chart references
    const chartsList = [];

    const registerChart = (chart) => {
        chartsList.push(chart);
    };

    window.addEventListener('themechanged', (e) => {
        const theme = getThemeColors();
        chartsList.forEach(chart => {
            if (chart && typeof chart.updateOptions === 'function') {
                chart.updateOptions({
                    theme: {
                        mode: theme.mode
                    },
                    chart: {
                        foreColor: theme.text
                    },
                    grid: {
                        borderColor: theme.grid
                    },
                    tooltip: {
                        theme: theme.mode
                    },
                    xaxis: {
                        labels: {
                            style: {
                                colors: theme.text
                            }
                        }
                    },
                    yaxis: {
                        labels: {
                            style: {
                                colors: theme.text
                            }
                        }
                    }
                });
            }
        });
    });

    return {
        PALETTES,
        getThemeColors,
        getDefaultOptions,
        mergeObjects,
        registerChart
    };
})();
