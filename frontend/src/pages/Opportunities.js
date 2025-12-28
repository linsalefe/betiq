import React, { useEffect, useMemo, useState, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  CircularProgress,
  useTheme,
  useMediaQuery,
  Fade,
  Alert,
  Paper,
  Tabs,
  Tab,
  Stack,
  Tooltip,
  IconButton,
  TextField,
  InputAdornment,
  FormControl,
  Select,
  MenuItem,
  Snackbar,
  Button,
  LinearProgress,
  Collapse,
  Skeleton,
} from '@mui/material';

import SportsIcon from '@mui/icons-material/Sports';
import SportsFootballIcon from '@mui/icons-material/SportsFootball';
import SportsTennisIcon from '@mui/icons-material/SportsTennis';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import RefreshIcon from '@mui/icons-material/Refresh';
import SearchIcon from '@mui/icons-material/Search';
import SortIcon from '@mui/icons-material/Sort';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';

import { getOpportunities } from '../services/api';

const Opportunities = () => {
  const [opportunities, setOpportunities] = useState([]);
  const [multiples, setMultiples] = useState([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [errorMsg, setErrorMsg] = useState('');
  const [activeTab, setActiveTab] = useState('simples');
  const [sportTab, setSportTab] = useState('all'); // all, football, nfl, tennis

  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('ev_desc');

  const [expandedIndex, setExpandedIndex] = useState(null);

  const [snack, setSnack] = useState({ open: false, message: '' });
  const [lastUpdated, setLastUpdated] = useState(null);

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const safeNumber = (v, fallback = 0) =>
    typeof v === 'number' && Number.isFinite(v) ? v : fallback;

  const formatMoney = (v) => {
    const n = safeNumber(v, 0);
    return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  };

  const formatDate = () => {
    const hoje = new Date();
    return hoje.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const formatTime = (d) => {
    if (!d) return '';
    return new Date(d).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  const loadOpportunities = useCallback(
    async ({ silent = false } = {}) => {
      try {
        if (!silent) setLoading(true);
        else setRefreshing(true);

        setErrorMsg('');

        const data = await getOpportunities(100);

        setOpportunities(Array.isArray(data?.opportunities) ? data.opportunities : []);
        setMultiples(Array.isArray(data?.multiples) ? data.multiples : []);
        setLastUpdated(new Date());
      } catch (error) {
        console.error('Erro ao carregar oportunidades:', error);
        setErrorMsg('Não foi possível carregar as oportunidades agora. Verifique sua conexão e tente novamente.');
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    []
  );

  useEffect(() => {
    loadOpportunities();
  }, [loadOpportunities]);

  const handleCopy = async (opp) => {
    const line = [
      `Jogo: ${opp?.match || '-'}`,
      `Competição: ${opp?.competition || '-'}`,
      `Mercado: ${opp?.market || '-'}`,
      `Odd: ${safeNumber(opp?.odds, 0).toFixed(2)}`,
      `EV: +${safeNumber(opp?.ev, 0).toFixed(1)}%`,
      `Prob: ${(safeNumber(opp?.probability, 0) * 100).toFixed(1)}%`,
      `Stake: ${formatMoney(opp?.stake)}`,
    ].join(' | ');

    try {
      await navigator.clipboard.writeText(line);
      setSnack({ open: true, message: 'Aposta copiada ✅' });
    } catch {
      setSnack({ open: true, message: 'Não consegui copiar automaticamente. (Seu navegador pode bloquear.)' });
    }
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Filtra por esporte
  const filterBySport = (opps) => {
    if (sportTab === 'all') return opps;
    
    return opps.filter(opp => {
      const sport = (opp?.sport || 'Football').toLowerCase();
      
      if (sportTab === 'football') {
        return sport === 'football' || sport === 'soccer';
      }
      if (sportTab === 'nfl') {
        return sport === 'nfl';
      }
      if (sportTab === 'tennis') {
        return sport === 'tennis';
      }
      return true;
    });
  };

  const filteredOpps = useMemo(() => {
    const q = search.trim().toLowerCase();

    // Primeiro filtra por esporte
    const bySport = filterBySport(opportunities);

    // Depois filtra por busca
    const base = bySport.filter((o) => {
      if (!q) return true;
      const hay = `${o?.match || ''} ${o?.competition || ''} ${o?.market || ''}`.toLowerCase();
      return hay.includes(q);
    });

    // Ordena
    const sorted = [...base].sort((a, b) => {
      const evA = safeNumber(a?.ev, 0);
      const evB = safeNumber(b?.ev, 0);
      const oddsA = safeNumber(a?.odds, 0);
      const oddsB = safeNumber(b?.odds, 0);
      const stakeA = safeNumber(a?.stake, 0);
      const stakeB = safeNumber(b?.stake, 0);
      const probA = safeNumber(a?.probability, 0);
      const probB = safeNumber(b?.probability, 0);

      switch (sortBy) {
        case 'ev_desc':
          return evB - evA;
        case 'odds_desc':
          return oddsB - oddsA;
        case 'stake_asc':
          return stakeA - stakeB;
        case 'prob_desc':
          return probB - probA;
        default:
          return evB - evA;
      }
    });

    return sorted;
  }, [opportunities, search, sortBy, sportTab]);

  // Contadores por esporte
  const sportCounts = useMemo(() => {
    const football = opportunities.filter(o => {
      const s = (o?.sport || 'Football').toLowerCase();
      return s === 'football' || s === 'soccer';
    }).length;
    
    const nfl = opportunities.filter(o => 
      (o?.sport || '').toLowerCase() === 'nfl'
    ).length;
    
    const tennis = opportunities.filter(o => 
      (o?.sport || '').toLowerCase() === 'tennis'
    ).length;

    return { football, nfl, tennis, all: opportunities.length };
  }, [opportunities]);

  const summary = useMemo(() => {
    const list = filteredOpps;
    if (!list.length) {
      return {
        bestEV: 0,
        avgEV: 0,
        totalStake: 0,
        totalReturn: 0,
      };
    }
    const bestEV = Math.max(...list.map((o) => safeNumber(o?.ev, 0)));
    const avgEV = list.reduce((acc, o) => acc + safeNumber(o?.ev, 0), 0) / list.length;
    const totalStake = list.reduce((acc, o) => acc + safeNumber(o?.stake, 0), 0);
    const totalReturn = list.reduce((acc, o) => acc + safeNumber(o?.potential_return, 0), 0);

    return { bestEV, avgEV, totalStake, totalReturn };
  }, [filteredOpps]);

  if (loading) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #F5F7FA 0%, #E8EEF2 100%)',
          px: 2,
        }}
      >
        <Box sx={{ width: '100%', maxWidth: 720 }}>
          <Stack spacing={2}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2 }}>
              <CircularProgress size={52} sx={{ color: 'primary.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Buscando oportunidades…
              </Typography>
            </Box>

            <Paper elevation={0} sx={{ borderRadius: 3, p: 2, border: '1px solid rgba(0,0,0,0.08)' }}>
              <Stack spacing={1.5}>
                <Skeleton height={36} />
                <Skeleton height={22} width="60%" />
                <Divider />
                <Skeleton height={120} />
              </Stack>
            </Paper>
          </Stack>
        </Box>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #F5F7FA 0%, #E8EEF2 100%)',
        py: { xs: 3, md: 4 },
      }}
    >
      <Container maxWidth="lg">
        {/* Header / Top Bar */}
        <Fade in timeout={600}>
          <Box sx={{ mb: 3 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: { xs: 'flex-start', sm: 'center' },
                justifyContent: 'space-between',
                gap: 2,
                flexWrap: 'wrap',
                mb: 1,
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <SportsIcon sx={{ color: 'primary.main', fontSize: isMobile ? 32 : 40 }} />
                <Box>
                  <Typography
                    variant={isMobile ? 'h4' : 'h3'}
                    sx={{
                      fontWeight: 800,
                      lineHeight: 1.05,
                      background: 'linear-gradient(135deg, #00A859 0%, #00763E 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                    }}
                  >
                    Oportunidades de Hoje
                  </Typography>

                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.7 }}>
                    <CalendarTodayIcon fontSize="small" color="action" />
                    <Typography variant="body2" color="text.secondary">
                      {formatDate()}
                      {lastUpdated ? ` • atualizado às ${formatTime(lastUpdated)}` : ''}
                    </Typography>
                  </Box>
                </Box>
              </Box>

              <Stack direction="row" spacing={1} alignItems="center">
                <Tooltip title="Voltar ao topo">
                  <IconButton onClick={scrollToTop} size="small" aria-label="voltar ao topo">
                    <ArrowUpwardIcon fontSize="small" />
                  </IconButton>
                </Tooltip>

                <Tooltip title="Atualizar oportunidades">
                  <span>
                    <IconButton
                      onClick={() => loadOpportunities({ silent: true })}
                      disabled={refreshing}
                      aria-label="atualizar"
                      sx={{
                        border: '1px solid rgba(0,0,0,0.08)',
                        borderRadius: 2,
                      }}
                    >
                      <RefreshIcon />
                    </IconButton>
                  </span>
                </Tooltip>
              </Stack>
            </Box>

            {/* Chips de contagem */}
            <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap', mt: 2 }}>
              <Chip
                label={`${opportunities.length} Apostas Simples`}
                sx={{ bgcolor: 'primary.main', color: 'white', fontWeight: 700 }}
              />
              <Chip
                label={`${multiples.length} Múltiplas`}
                sx={{ bgcolor: 'secondary.main', color: 'white', fontWeight: 700 }}
              />
              <Tooltip title="As oportunidades aqui são filtradas por +EV. Nem todo dia aparece coisa boa — isso é ótimo pra disciplina.">
                <Chip
                  icon={<InfoOutlinedIcon sx={{ color: 'white !important' }} />}
                  label="Como usar"
                  sx={{
                    bgcolor: 'text.primary',
                    color: 'white',
                    fontWeight: 700,
                    cursor: 'help',
                  }}
                />
              </Tooltip>
            </Box>

            {/* Loading de refresh discreto */}
            {refreshing && (
              <Box sx={{ mt: 2 }}>
                <LinearProgress sx={{ borderRadius: 999 }} />
              </Box>
            )}
          </Box>
        </Fade>

        {/* Tabs: Simples vs Múltiplas */}
        <Paper
          elevation={0}
          sx={{
            borderRadius: 3,
            border: '1px solid rgba(0,0,0,0.08)',
            overflow: 'hidden',
            mb: 2,
          }}
        >
          <Tabs
            value={activeTab}
            onChange={(_, v) => setActiveTab(v)}
            variant="fullWidth"
            sx={{
              '& .MuiTab-root': { fontWeight: 800 },
            }}
          >
            <Tab value="simples" label={`Simples (${opportunities.length})`} />
            <Tab value="multiples" label={`Múltiplas (${multiples.length})`} />
          </Tabs>
        </Paper>

        {/* Tabs de ESPORTE (apenas para simples) */}
        {activeTab === 'simples' && (
          <Fade in timeout={500}>
            <Paper
              elevation={0}
              sx={{
                borderRadius: 3,
                border: '1px solid rgba(0,0,0,0.08)',
                overflow: 'hidden',
                mb: 2,
              }}
            >
              <Tabs
                value={sportTab}
                onChange={(_, v) => setSportTab(v)}
                variant="fullWidth"
                sx={{
                  '& .MuiTab-root': { fontWeight: 800 },
                  bgcolor: 'rgba(0,168,89,0.04)',
                }}
              >
                <Tab 
                  value="all" 
                  icon={<SportsIcon />} 
                  iconPosition="start"
                  label={`Todos (${sportCounts.all})`} 
                />
                <Tab 
                  value="football" 
                  icon={<SportsIcon />} 
                  iconPosition="start"
                  label={`Futebol (${sportCounts.football})`} 
                />
                <Tab 
                  value="nfl" 
                  icon={<SportsFootballIcon />} 
                  iconPosition="start"
                  label={`NFL (${sportCounts.nfl})`} 
                />
                <Tab 
                  value="tennis" 
                  icon={<SportsTennisIcon />} 
                  iconPosition="start"
                  label={`Tênis (${sportCounts.tennis})`} 
                />
              </Tabs>
            </Paper>
          </Fade>
        )}

        {/* Controles (busca + ordenação) */}
        {activeTab === 'simples' && (
          <Fade in timeout={500}>
            <Paper
              elevation={0}
              sx={{
                borderRadius: 3,
                border: '1px solid rgba(0,0,0,0.08)',
                p: 2,
                mb: 3,
              }}
            >
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={7}>
                  <TextField
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    fullWidth
                    placeholder="Buscar por jogo, competição ou mercado…"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <SearchIcon color="action" />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Grid>

                <Grid item xs={12} md={5}>
                  <FormControl fullWidth>
                    <Select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      startAdornment={
                        <InputAdornment position="start">
                          <SortIcon color="action" />
                        </InputAdornment>
                      }
                      sx={{ pl: 1 }}
                    >
                      <MenuItem value="ev_desc">Ordenar: Maior EV</MenuItem>
                      <MenuItem value="prob_desc">Ordenar: Maior Probabilidade</MenuItem>
                      <MenuItem value="odds_desc">Ordenar: Maior Odd</MenuItem>
                      <MenuItem value="stake_asc">Ordenar: Menor Stake</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </Paper>
          </Fade>
        )}

        {/* Erro */}
        {!!errorMsg && (
          <Fade in timeout={400}>
            <Alert
              severity="error"
              sx={{
                borderRadius: 3,
                mb: 3,
                '& .MuiAlert-icon': { fontSize: 28 },
              }}
              action={
                <Button color="inherit" size="small" onClick={() => loadOpportunities({ silent: true })}>
                  Tentar novamente
                </Button>
              }
            >
              <Typography variant="body1" sx={{ fontWeight: 700 }}>
                Ops…
              </Typography>
              <Typography variant="body2">{errorMsg}</Typography>
            </Alert>
          </Fade>
        )}

        {/* Conteúdo: SIMPLES */}
        {activeTab === 'simples' && (
          <>
            {/* Empty state */}
            {filteredOpps.length === 0 ? (
              <Fade in timeout={800}>
                <Alert
                  severity="info"
                  sx={{
                    borderRadius: 3,
                    fontSize: '1rem',
                    '& .MuiAlert-icon': { fontSize: 28 },
                  }}
                  action={
                    <Button variant="contained" onClick={() => loadOpportunities({ silent: true })}>
                      Atualizar
                    </Button>
                  }
                >
                  <Typography variant="h6" sx={{ mb: 1, fontWeight: 800 }}>
                    Nenhuma oportunidade com bom +EV 
                    {sportTab !== 'all' && ` em ${
                      sportTab === 'football' ? 'Futebol' :
                      sportTab === 'nfl' ? 'NFL' : 'Tênis'
                    }`}
                  </Typography>
                  <Typography variant="body2">
                    Isso é normal — e faz parte da disciplina do método. Em dias com poucos jogos (ex.: véspera de feriado),
                    o melhor "trade" pode ser não entrar em nenhum.
                  </Typography>
                </Alert>
              </Fade>
            ) : (
              <>
                {/* Resumo (quick stats) */}
                <Fade in timeout={650}>
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={12} md={3}>
                      <Paper
                        elevation={0}
                        sx={{
                          borderRadius: 3,
                          border: '1px solid rgba(0,0,0,0.08)',
                          p: 2,
                          height: '100%',
                        }}
                      >
                        <Stack direction="row" spacing={1.5} alignItems="center">
                          <TrendingUpIcon color="primary" />
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Melhor EV
                            </Typography>
                            <Typography variant="h6" sx={{ fontWeight: 900 }}>
                              +{safeNumber(summary.bestEV, 0).toFixed(1)}%
                            </Typography>
                          </Box>
                        </Stack>
                      </Paper>
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <Paper
                        elevation={0}
                        sx={{
                          borderRadius: 3,
                          border: '1px solid rgba(0,0,0,0.08)',
                          p: 2,
                          height: '100%',
                        }}
                      >
                        <Stack direction="row" spacing={1.5} alignItems="center">
                          <TrendingUpIcon color="action" />
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              EV médio
                            </Typography>
                            <Typography variant="h6" sx={{ fontWeight: 900 }}>
                              +{safeNumber(summary.avgEV, 0).toFixed(1)}%
                            </Typography>
                          </Box>
                        </Stack>
                      </Paper>
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <Paper
                        elevation={0}
                        sx={{
                          borderRadius: 3,
                          border: '1px solid rgba(0,0,0,0.08)',
                          p: 2,
                          height: '100%',
                        }}
                      >
                        <Stack direction="row" spacing={1.5} alignItems="center">
                          <AttachMoneyIcon color="primary" />
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Stake total (sug.)
                            </Typography>
                            <Typography variant="h6" sx={{ fontWeight: 900 }}>
                              {formatMoney(summary.totalStake)}
                            </Typography>
                          </Box>
                        </Stack>
                      </Paper>
                    </Grid>

                    <Grid item xs={12} md={3}>
                      <Paper
                        elevation={0}
                        sx={{
                          borderRadius: 3,
                          border: '1px solid rgba(0,0,0,0.08)',
                          p: 2,
                          height: '100%',
                        }}
                      >
                        <Stack direction="row" spacing={1.5} alignItems="center">
                          <AttachMoneyIcon color="action" />
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Retorno potencial (soma)
                            </Typography>
                            <Typography variant="h6" sx={{ fontWeight: 900 }}>
                              {formatMoney(summary.totalReturn)}
                            </Typography>
                          </Box>
                        </Stack>
                      </Paper>
                    </Grid>
                  </Grid>
                </Fade>

                {/* Lista de oportunidades */}
                <Grid container spacing={3}>
                  {filteredOpps.map((opp, index) => {
                    const odds = safeNumber(opp?.odds, 0);
                    const ev = safeNumber(opp?.ev, 0);
                    const prob = safeNumber(opp?.probability, 0);
                    const stake = safeNumber(opp?.stake, 0);
                    const potentialReturn = safeNumber(opp?.potential_return, 0);
                    const isExpanded = expandedIndex === index;
                    const sport = opp?.sport || 'Football';

                    return (
                      <Grid item xs={12} md={6} key={`${opp?.match || 'opp'}-${index}`}>
                        <Fade in timeout={520 + index * 70}>
                          <Card
                            elevation={0}
                            sx={{
                              borderRadius: 3,
                              border: '1px solid rgba(0,0,0,0.08)',
                              transition: 'all 0.25s ease',
                              overflow: 'hidden',
                              '&:hover': {
                                transform: 'translateY(-4px)',
                                boxShadow: '0 8px 24px rgba(0,168,89,0.15)',
                              },
                            }}
                          >
                            <CardContent sx={{ p: 3 }}>
                              {/* Cabeçalho */}
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2, mb: 1.5 }}>
                                <Box sx={{ minWidth: 0 }}>
                                  <Typography
                                    variant="h6"
                                    sx={{
                                      fontWeight: 900,
                                      color: 'text.primary',
                                      overflow: 'hidden',
                                      textOverflow: 'ellipsis',
                                      whiteSpace: 'nowrap',
                                    }}
                                    title={opp?.match || ''}
                                  >
                                    {opp?.match || '-'}
                                  </Typography>
                                  <Typography
                                    variant="caption"
                                    sx={{
                                      color: 'text.secondary',
                                      textTransform: 'uppercase',
                                      letterSpacing: 0.6,
                                    }}
                                  >
                                    {opp?.competition || '-'}
                                  </Typography>
                                </Box>

                                <Stack direction="column" spacing={0.8} alignItems="flex-end">
                                  <Chip
                                    label={`+${ev.toFixed(1)}%`}
                                    size="small"
                                    sx={{
                                      bgcolor: 'success.main',
                                      color: 'white',
                                      fontWeight: 900,
                                    }}
                                  />
                                  <Chip
                                    label={opp?.market || 'Mercado'}
                                    size="small"
                                    sx={{
                                      bgcolor: 'rgba(0,0,0,0.06)',
                                      fontWeight: 800,
                                    }}
                                  />
                                  <Chip
                                    label={`🏢 ${opp?.bookmaker || 'N/A'}`}
                                    size="small"
                                    sx={{
                                      bgcolor: 'rgba(25, 118, 210, 0.1)',
                                      color: '#1976d2',
                                      fontWeight: 700,
                                    }}
                                  />
                                  <Chip
                                    label={sport}
                                    size="small"
                                    icon={
                                      sport === 'NFL' ? <SportsFootballIcon /> :
                                      sport === 'Tennis' ? <SportsTennisIcon /> :
                                      <SportsIcon />
                                    }
                                    sx={{
                                      bgcolor: 
                                        sport === 'NFL' ? 'rgba(237, 108, 2, 0.1)' :
                                        sport === 'Tennis' ? 'rgba(156, 39, 176, 0.1)' :
                                        'rgba(0, 168, 89, 0.1)',
                                      fontWeight: 700,
                                      fontSize: '0.7rem',
                                    }}
                                  />
                                </Stack>
                              </Box>

                              {/* Linha de "scan" rápida */}
                              <Grid container spacing={2} sx={{ mb: 1.5 }}>
                                <Grid item xs={4}>
                                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                                    Odd
                                  </Typography>
                                  <Typography variant="body1" fontWeight={900} color="primary.main">
                                    {odds.toFixed(2)}
                                  </Typography>
                                </Grid>

                                <Grid item xs={4}>
                                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                                    Prob.
                                  </Typography>
                                  <Typography variant="body2" fontWeight={800}>
                                    {(prob * 100).toFixed(1)}%
                                  </Typography>
                                </Grid>

                                <Grid item xs={4}>
                                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                                    Stake
                                  </Typography>
                                  <Typography variant="body2" fontWeight={800}>
                                    {formatMoney(stake)}
                                  </Typography>
                                </Grid>
                              </Grid>

                              {/* Barra de probabilidade */}
                              <Box sx={{ mb: 2 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.8 }}>
                                  <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>
                                    Confiança do modelo
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>
                                    {(prob * 100).toFixed(1)}%
                                  </Typography>
                                </Box>
                                <LinearProgress
                                  variant="determinate"
                                  value={Math.max(0, Math.min(100, prob * 100))}
                                  sx={{ height: 10, borderRadius: 999 }}
                                />
                              </Box>

                              {/* Caixa stake / retorno */}
                              <Box
                                sx={{
                                  mt: 1,
                                  p: 2,
                                  borderRadius: 2,
                                  background: 'linear-gradient(135deg, #00A859 0%, #00C46A 100%)',
                                }}
                              >
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                  <Box>
                                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                                      Stake sugerido
                                    </Typography>
                                    <Typography variant="h6" sx={{ color: 'white', fontWeight: 900 }}>
                                      {formatMoney(stake)}
                                    </Typography>
                                  </Box>
                                  <Box sx={{ textAlign: 'right' }}>
                                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                                      Retorno potencial
                                    </Typography>
                                    <Typography variant="h6" sx={{ color: 'white', fontWeight: 900 }}>
                                      {formatMoney(potentialReturn)}
                                    </Typography>
                                  </Box>
                                </Box>
                              </Box>

                              {/* Ações */}
                              <Stack direction="row" spacing={1} sx={{ mt: 2 }} alignItems="center">
                                <Button
                                  variant="contained"
                                  onClick={() => handleCopy(opp)}
                                  startIcon={<ContentCopyIcon />}
                                  sx={{ fontWeight: 900, borderRadius: 2 }}
                                >
                                  Copiar aposta
                                </Button>

                                <Button
                                  variant="text"
                                  onClick={() => setExpandedIndex(isExpanded ? null : index)}
                                  sx={{ fontWeight: 900, borderRadius: 2 }}
                                >
                                  {isExpanded ? 'Ocultar detalhes' : 'Ver detalhes'}
                                </Button>
                              </Stack>

                              {/* Detalhes expansíveis */}
                              <Collapse in={isExpanded}>
                                <Divider sx={{ my: 2 }} />

                                <Grid container spacing={2}>
                                  <Grid item xs={6}>
                                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                                      Prob. implícita (odd)
                                    </Typography>
                                    <Typography variant="body2" fontWeight={900}>
                                      {odds > 0 ? `${((1 / odds) * 100).toFixed(1)}%` : '-'}
                                    </Typography>
                                  </Grid>

                                  <Grid item xs={6}>
                                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                                      "Edge" (Prob - Impl.)
                                    </Typography>
                                    <Typography variant="body2" fontWeight={900}>
                                      {odds > 0 ? `${(((prob - 1 / odds) * 100) || 0).toFixed(1)}%` : '-'}
                                    </Typography>
                                  </Grid>

                                  <Grid item xs={12}>
                                    <Paper
                                      elevation={0}
                                      sx={{
                                        borderRadius: 2,
                                        p: 1.5,
                                        border: '1px dashed rgba(0,0,0,0.18)',
                                        bgcolor: 'rgba(0,0,0,0.02)',
                                      }}
                                    >
                                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>
                                        Dica rápida
                                      </Typography>
                                      <Typography variant="body2" sx={{ fontWeight: 700 }}>
                                        Se você for entrar, priorize as maiores EV com boa probabilidade — e evite "forçar"
                                        entrada só pra ter ação.
                                      </Typography>
                                    </Paper>
                                  </Grid>
                                </Grid>
                              </Collapse>
                            </CardContent>
                          </Card>
                        </Fade>
                      </Grid>
                    );
                  })}
                </Grid>
              </>
            )}
          </>
        )}

        {/* Conteúdo: MÚLTIPLAS */}
        {activeTab === 'multiples' && (
          <Fade in timeout={650}>
            <Box sx={{ mt: 1 }}>
              {multiples.length === 0 ? (
                <Alert
                  severity="info"
                  sx={{ borderRadius: 3, '& .MuiAlert-icon': { fontSize: 28 } }}
                  action={
                    <Button variant="contained" onClick={() => loadOpportunities({ silent: true })}>
                      Atualizar
                    </Button>
                  }
                >
                  <Typography variant="h6" sx={{ mb: 1, fontWeight: 800 }}>
                    Sem múltiplas estratégicas hoje
                  </Typography>
                  <Typography variant="body2">
                    Quando aparecer, use como opção extra — mas trate múltipla como "perfil de risco" mais alto.
                  </Typography>
                </Alert>
              ) : (
                <Grid container spacing={3}>
                  {multiples.map((multiple, index) => {
                    const combinedOdds = safeNumber(multiple?.combined_odds, 0);
                    const legs = Array.isArray(multiple?.legs) ? multiple.legs : [];

                    return (
                      <Grid item xs={12} key={`multiple-${index}`}>
                        <Fade in timeout={720 + index * 90}>
                          <Card
                            elevation={0}
                            sx={{
                              borderRadius: 3,
                              border: '2px solid',
                              borderColor: 'secondary.main',
                              background: 'linear-gradient(135deg, #FFF9F0 0%, #FFFFFF 100%)',
                              overflow: 'hidden',
                            }}
                          >
                            <CardContent sx={{ p: 3 }}>
                              <Box sx={{ display: 'flex', justifyContent: 'space-between', gap: 2, flexWrap: 'wrap' }}>
                                <Box>
                                  <Typography variant="h6" fontWeight={900} sx={{ mb: 0.5 }}>
                                    Múltipla #{index + 1}
                                  </Typography>
                                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 700 }}>
                                    {multiple?.description || `${legs.length} pernas combinadas`}
                                  </Typography>
                                </Box>

                                <Chip
                                  label={`Odd combinada: ${combinedOdds ? combinedOdds.toFixed(2) : '-'}`}
                                  sx={{
                                    bgcolor: 'secondary.main',
                                    color: 'white',
                                    fontWeight: 900,
                                    alignSelf: 'flex-start',
                                  }}
                                />
                              </Box>

                              {legs.length > 0 && (
                                <>
                                  <Divider sx={{ my: 2 }} />
                                  <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 900 }}>
                                    Pernas
                                  </Typography>
                                  <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={{ mt: 1 }}>
                                    {legs.map((leg, i) => {
                                      const label =
                                        typeof leg === 'string'
                                          ? leg
                                          : leg?.selection || leg?.market || leg?.match || `Perna ${i + 1}`;
                                      return (
                                        <Chip
                                          key={`leg-${index}-${i}`}
                                          label={label}
                                          sx={{ fontWeight: 800 }}
                                          variant="outlined"
                                        />
                                      );
                                    })}
                                  </Stack>
                                </>
                              )}
                            </CardContent>
                          </Card>
                        </Fade>
                      </Grid>
                    );
                  })}
                </Grid>
              )}
            </Box>
          </Fade>
        )}

        {/* Snackbar */}
        <Snackbar
          open={snack.open}
          autoHideDuration={2200}
          onClose={() => setSnack((s) => ({ ...s, open: false }))}
          message={snack.message}
        />
      </Container>
    </Box>
  );
};

export default Opportunities;