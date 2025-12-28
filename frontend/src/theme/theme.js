import { createTheme, responsiveFontSizes } from '@mui/material/styles';

let theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#00A859',
      light: '#33B973',
      dark: '#00763E',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#212121',
      light: '#484848',
      dark: '#000000',
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#4CAF50',
      light: '#81C784',
      dark: '#388E3C',
    },
    error: {
      main: '#F44336',
      light: '#E57373',
      dark: '#D32F2F',
    },
    warning: {
      main: '#FF9800',
      light: '#FFB74D',
      dark: '#F57C00',
    },
    background: {
      default: '#F5F7FA',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#212121',
      secondary: '#757575',
    },
  },

  // Tipografia: mais clean, legível e com hierarquia forte (UX máxima)
  typography: {
    fontFamily: [
      'Inter',
      'system-ui',
      '-apple-system',
      'Segoe UI',
      'Roboto',
      'Helvetica',
      'Arial',
      'sans-serif',
    ].join(','),

    fontSize: 14,
    htmlFontSize: 16,

    h1: { fontWeight: 800, letterSpacing: '-0.04em', lineHeight: 1.05 },
    h2: { fontWeight: 800, letterSpacing: '-0.035em', lineHeight: 1.08 },
    h3: { fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.12 },
    h4: { fontWeight: 800, letterSpacing: '-0.025em', lineHeight: 1.15 },
    h5: { fontWeight: 750, letterSpacing: '-0.02em', lineHeight: 1.2 },
    h6: { fontWeight: 700, letterSpacing: '-0.015em', lineHeight: 1.25 },

    subtitle1: { fontWeight: 650, letterSpacing: '-0.01em', lineHeight: 1.35 },
    subtitle2: { fontWeight: 600, letterSpacing: '-0.005em', lineHeight: 1.35 },

    body1: { fontWeight: 500, letterSpacing: '-0.005em', lineHeight: 1.65 },
    body2: { fontWeight: 500, letterSpacing: '0em', lineHeight: 1.6 },

    caption: { fontWeight: 650, letterSpacing: '0.02em', lineHeight: 1.35 },
    overline: { fontWeight: 750, letterSpacing: '0.08em', lineHeight: 1.2 },

    button: { textTransform: 'none', fontWeight: 800, letterSpacing: '0em' },
  },

  shape: {
    borderRadius: 16,
  },

  // CORRIGIDO: o MUI exige array com 25 níveis (0..24)
  shadows: [
    'none', // 0
    '0px 2px 4px rgba(0, 0, 0, 0.05)', // 1
    '0px 4px 8px rgba(0, 0, 0, 0.08)', // 2
    '0px 8px 16px rgba(0, 0, 0, 0.10)', // 3
    '0px 12px 24px rgba(0, 0, 0, 0.12)', // 4
    '0px 16px 32px rgba(0, 0, 0, 0.14)', // 5
    '0px 20px 40px rgba(0, 0, 0, 0.16)', // 6
    '0px 24px 48px rgba(0, 0, 0, 0.18)', // 7
    '0px 2px 4px rgba(0, 0, 0, 0.05)', // 8
    '0px 4px 8px rgba(0, 0, 0, 0.08)', // 9
    '0px 8px 16px rgba(0, 0, 0, 0.10)', // 10
    '0px 12px 24px rgba(0, 0, 0, 0.12)', // 11
    '0px 16px 32px rgba(0, 0, 0, 0.14)', // 12
    '0px 20px 40px rgba(0, 0, 0, 0.16)', // 13
    '0px 24px 48px rgba(0, 0, 0, 0.18)', // 14
    '0px 2px 4px rgba(0, 0, 0, 0.05)', // 15
    '0px 4px 8px rgba(0, 0, 0, 0.08)', // 16
    '0px 8px 16px rgba(0, 0, 0, 0.10)', // 17
    '0px 12px 24px rgba(0, 0, 0, 0.12)', // 18
    '0px 16px 32px rgba(0, 0, 0, 0.14)', // 19
    '0px 20px 40px rgba(0,  0, 0, 0.16)', // 20
    '0px 24px 48px rgba(0, 0, 0, 0.18)', // 21
    '0px 2px 4px rgba(0, 0, 0, 0.05)', // 22
    '0px 4px 8px rgba(0, 0, 0, 0.08)', // 23
    '0px 8px 16px rgba(0, 0, 0, 0.10)', // 24
  ],

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        html: { WebkitFontSmoothing: 'antialiased', MozOsxFontSmoothing: 'grayscale' },
        body: { textRendering: 'optimizeLegibility' },
        // melhora seleção de texto
        '::selection': { background: 'rgba(0,168,89,0.18)' },
      },
    },

    // Cards mais premium (sem mudar cores)
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          transition: 'transform 0.25s ease, box-shadow 0.25s ease',
          willChange: 'transform',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0px 12px 24px rgba(0, 0, 0, 0.15)',
          },
        },
      },
    },

    // Botões: clean, sem uppercase, com microinteração suave
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          padding: '10px 18px',
          fontSize: '0.95rem',
          boxShadow: 'none',
          textTransform: 'none',
          transition: 'transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0px 8px 16px rgba(0, 168, 89, 0.25)',
          },
          '&:active': {
            transform: 'translateY(0px)',
            filter: 'brightness(0.98)',
          },
        },
      },
    },

    // Paper: remove “backgroundImage” e deixa clean
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 20,
          backgroundImage: 'none',
        },
      },
    },

    // Chips mais modernos (pill)
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 999,
          fontWeight: 800,
        },
      },
    },

    // Inputs: mais premium
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 14,
          backgroundColor: 'rgba(0,0,0,0.02)',
          transition: 'background-color 0.18s ease',
          '&:hover': {
            backgroundColor: 'rgba(0,0,0,0.04)',
          },
          '&.Mui-focused': {
            backgroundColor: '#FFFFFF',
          },
        },
        input: {
          fontWeight: 550,
        },
      },
    },

    // Labels e helper text mais legíveis
    MuiFormLabel: {
      styleOverrides: {
        root: {
          fontWeight: 700,
        },
      },
    },

    // Tabelas mais clean
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontWeight: 900,
          letterSpacing: '-0.01em',
        },
        body: {
          fontWeight: 550,
        },
      },
    },

    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          borderRadius: 12,
          fontWeight: 700,
        },
      },
    },
  },
});

// Tipografia responsiva (fica perfeita do mobile ao desktop)
theme = responsiveFontSizes(theme, { factor: 2.2 });

export default theme;
