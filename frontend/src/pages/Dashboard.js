import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  LinearProgress,
  useTheme,
  useMediaQuery,
  Fade,
  Zoom,
  IconButton,
  Tooltip,
  Stack,
  Divider,
  TextField,
  InputAdornment,
  Skeleton,
  Collapse,
  Snackbar,
  Button,
} from '@mui/material';

import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import FlagIcon from '@mui/icons-material/Flag';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import RefreshIcon from '@mui/icons-material/Refresh';
import SearchIcon from '@mui/icons-material/Search';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import PendingActionsIcon from '@mui/icons-material/PendingActions';
import CasinoIcon from '@mui/icons-material/Casino';
import InsightsIcon from '@mui/icons-material/Insights';

import { getStatistics, getHistory, getCurrentPhase } from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [phase, setPhase] = useState(null);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const [errorMsg, setErrorMsg] = useState('');
  const [snack, setSnack] = useState({ open: false, message: '' });

  const [lastUpdated, setLastUpdated] = useState(null);

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));

  useEffect(() => {
    fetchData({ initial: true });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchData = useCallback(async ({ initial = false } = {}) => {
    try {
      if (initial) setLoading(true);
      else setRefreshing(true);

      setErrorMsg('');

      const [statsData, historyData, phaseData] = await Promise.all([
        getStatistics(),
        getHistory(10),
        getCurrentPhase(),
      ]);

      setStats(statsData);
      setHistory(Array.isArray(historyData) ? historyData : []);
      setPhase(phaseData);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      setErrorMsg('Não foi possível carregar os dados do dashboard agora. Tente novamente.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  const formatMoney = (v) => {
    const n = typeof v === 'number' && Number.isFinite(v) ? v : 0;
    return n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  };

  const formatTime = (d) => {
    if (!d) return '';
    return new Date(d).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  const scrollToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' });

  const getStatusChip = (status) => {
    const statusConfig = {
      won: { label: 'Vitória', color: 'success', icon: '✅' },
      lost: { label: 'Derrota', color: 'error', icon: '❌' },
      pending: { label: 'Pendente', color: 'warning', icon: '⏳' },
      void: { label: 'Anulada', color: 'default', icon: '⚪' },
    };

    const config = statusConfig[status] || statusConfig.pending;
    return (
      <Chip
        label={`${config.icon} ${isMobile ? '' : config.label}`}
        color={config.color}
        size="small"
        sx={{ fontWeight: 700 }}
      />
    );
  };

  const profit = stats?.profit || 0;
  const isProfit = profit >= 0;

  // ====== Insights rápidos (derivados do history, sem precisar do backend) ======
  const derived = useMemo(() => {
    const list = Array.isArray(history) ? history : [];
    const totalBets = list.length;

    const pendingCount = list.filter((b) => b?.status === 'pending').length;
    const wonCount = list.filter((b) => b?.status === 'won').length;
    const lostCount = list.filter((b) => b?.status === 'lost').length;

    const avgOdds =
      totalBets > 0
        ? list.reduce((acc, b) => acc + (Number(b?.odds) || 0), 0) / totalBets
        : 0;

    const totalStake = list.reduce((acc, b) => acc + (Number(b?.stake) || 0), 0);

    // streak simples com base no histórico (mais recente primeiro)
    const streak = (() => {
      let s = 0;
      for (const b of list) {
        if (b?.status === 'won') s += 1;
        else if (b?.status === 'lost') break;
        else continue;
      }
      return s;
    })();

    return { totalBets, pendingCount, wonCount, lostCount, avgOdds, totalStake, streak };
  }, [history]);

  // ====== Filtragem do histórico ======
  const filteredHistory = useMemo(() => {
    const q = search.trim().toLowerCase();
    return history
      .filter((b) => {
        if (statusFilter === 'all') return true;
        return b?.status === statusFilter;
      })
      .filter((b) => {
        if (!q) return true;
        const hay = `${b?.match || ''} ${b?.market || ''}`.toLowerCase();
        return hay.includes(q);
      });
  }, [history, statusFilter, search]);

  // ====== Skeleton loading ======
  if (loading) {
    return (
      <Box
        sx={{
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #F5F7FA 0%, #E8EEF2 100%)',
          py: { xs: 2, md: 4 },
        }}
      >
        <Container maxWidth="lg">
          <Stack spacing={2}>
            <Box>
              <Skeleton width={220} height={48} />
              <Skeleton width={320} height={22} />
            </Box>

            <Grid container spacing={{ xs: 2, md: 3 }}>
              {[1, 2, 3, 4].map((k) => (
                <Grid item xs={6} md={3} key={k}>
                  <Paper
                    elevation={0}
                    sx={{ borderRadius: 3, border: '1px solid rgba(0,0,0,0.08)', p: 2 }}
                  >
                    <Skeleton height={24} width="70%" />
                    <Skeleton height={44} />
                    <Skeleton height={16} width="55%" />
                  </Paper>
                </Grid>
              ))}
            </Grid>

            <Paper elevation={0} sx={{ borderRadius: 3, border: '1px solid rgba(0,0,0,0.08)', p: 2 }}>
              <Skeleton height={32} width={240} />
              <Divider sx={{ my: 2 }} />
              <Skeleton height={220} />
            </Paper>
          </Stack>
        </Container>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #F5F7FA 0%, #E8EEF2 100%)',
        pb: { xs: 4, md: 6 },
      }}
    >
      <Container maxWidth="lg" sx={{ pt: { xs: 2, md: 4 } }}>
        {/* Header + Top actions */}
        <Fade in timeout={700}>
          <Box sx={{ mb: 3 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: { xs: 'flex-start', sm: 'center' },
                justifyContent: 'space-between',
                gap: 2,
                flexWrap: 'wrap',
              }}
            >
              <Box>
                <Typography
                  variant={isMobile ? 'h5' : 'h4'}
                  sx={{
                    fontWeight: 900,
                    background: 'linear-gradient(135deg, #00A859 0%, #00763E 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    mb: 0.6,
                  }}
                >
                  📊 Dashboard
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Visão geral das suas operações
                  {lastUpdated ? ` • atualizado às ${formatTime(lastUpdated)}` : ''}
                </Typography>
              </Box>

              <Stack direction="row" spacing={1} alignItems="center">
                <Tooltip title="Voltar ao topo">
                  <IconButton
                    onClick={scrollToTop}
                    sx={{ bgcolor: 'white', border: '1px solid rgba(0,0,0,0.08)', borderRadius: 2 }}
                  >
                    <ArrowUpwardIcon fontSize="small" />
                  </IconButton>
                </Tooltip>

                <Tooltip title="Atualizar dados">
                  <span>
                    <IconButton
                      onClick={() => fetchData({ initial: false })}
                      disabled={refreshing}
                      sx={{ bgcolor: 'white', border: '1px solid rgba(0,0,0,0.08)', borderRadius: 2 }}
                    >
                      <RefreshIcon />
                    </IconButton>
                  </span>
                </Tooltip>
              </Stack>
            </Box>

            <Collapse in={refreshing}>
              <Box sx={{ mt: 2 }}>
                <LinearProgress sx={{ borderRadius: 999 }} />
              </Box>
            </Collapse>

            {!!errorMsg && (
              <Paper
                elevation={0}
                sx={{
                  mt: 2,
                  p: 1.5,
                  borderRadius: 3,
                  border: '1px solid rgba(0,0,0,0.08)',
                  bgcolor: 'rgba(255,0,0,0.04)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: 2,
                }}
              >
                <Typography variant="body2" sx={{ fontWeight: 800 }}>
                  {errorMsg}
                </Typography>
                <Button
                  variant="contained"
                  onClick={() => fetchData({ initial: false })}
                  startIcon={<RefreshIcon />}
                  sx={{ fontWeight: 900, borderRadius: 2 }}
                >
                  Tentar novamente
                </Button>
              </Paper>
            )}
          </Box>
        </Fade>

        {/* Cards de Métricas */}
        <Grid container spacing={{ xs: 2, md: 3 }} sx={{ mb: 3 }}>
          {/* Banca */}
          <Grid item xs={6} md={3}>
            <Zoom in timeout={520}>
              <Card
                elevation={0}
                sx={{
                  background: 'linear-gradient(135deg, #00A859 0%, #00C46A 100%)',
                  color: 'white',
                  position: 'relative',
                  overflow: 'hidden',
                  borderRadius: 3,
                  transition: 'all 0.25s ease',
                  '&:hover': { transform: 'translateY(-3px)', boxShadow: '0 10px 24px rgba(0,168,89,0.18)' },
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    right: 0,
                    width: '100px',
                    height: '100px',
                    background: 'rgba(255,255,255,0.1)',
                    borderRadius: '50%',
                    transform: 'translate(30%, -30%)',
                  },
                }}
              >
                <CardContent sx={{ p: { xs: 2, md: 3 } }}>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                    <AccountBalanceWalletIcon sx={{ fontSize: isMobile ? 20 : 24 }} />
                    <Typography variant={isMobile ? 'body2' : 'h6'} sx={{ fontWeight: 800 }}>
                      Banca
                    </Typography>
                  </Stack>
                  <Typography variant={isMobile ? 'h5' : 'h4'} sx={{ fontWeight: 900, letterSpacing: '-0.02em' }}>
                    {formatMoney(phase?.bankroll)}
                  </Typography>
                </CardContent>
              </Card>
            </Zoom>
          </Grid>

          {/* Balanço */}
          <Grid item xs={6} md={3}>
            <Zoom in timeout={620}>
              <Card
                elevation={0}
                sx={{
                  background: isProfit
                    ? 'linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%)'
                    : 'linear-gradient(135deg, #F44336 0%, #EF5350 100%)',
                  color: 'white',
                  position: 'relative',
                  overflow: 'hidden',
                  borderRadius: 3,
                  transition: 'all 0.25s ease',
                  '&:hover': { transform: 'translateY(-3px)', boxShadow: '0 10px 24px rgba(0,0,0,0.14)' },
                }}
              >
                <CardContent sx={{ p: { xs: 2, md: 3 } }}>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                    {isProfit ? (
                      <TrendingUpIcon sx={{ fontSize: isMobile ? 20 : 24 }} />
                    ) : (
                      <TrendingDownIcon sx={{ fontSize: isMobile ? 20 : 24 }} />
                    )}
                    <Typography variant={isMobile ? 'body2' : 'h6'} sx={{ fontWeight: 800 }}>
                      Balanço
                    </Typography>
                  </Stack>
                  <Typography variant={isMobile ? 'h5' : 'h4'} sx={{ fontWeight: 900, letterSpacing: '-0.02em' }}>
                    {formatMoney(profit)}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.92, fontWeight: 700 }}>
                    ROI: {stats?.roi?.toFixed(2) || '0.00'}%
                  </Typography>
                </CardContent>
              </Card>
            </Zoom>
          </Grid>

          {/* Win Rate */}
          <Grid item xs={6} md={3}>
            <Zoom in timeout={720}>
              <Card
                elevation={0}
                sx={{
                  background: 'linear-gradient(135deg, #2196F3 0%, #42A5F5 100%)',
                  color: 'white',
                  borderRadius: 3,
                  transition: 'all 0.25s ease',
                  '&:hover': { transform: 'translateY(-3px)', boxShadow: '0 10px 24px rgba(33,150,243,0.18)' },
                }}
              >
                <CardContent sx={{ p: { xs: 2, md: 3 } }}>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                    <EmojiEventsIcon sx={{ fontSize: isMobile ? 20 : 24 }} />
                    <Typography variant={isMobile ? 'body2' : 'h6'} sx={{ fontWeight: 800 }}>
                      Win Rate
                    </Typography>
                  </Stack>
                  <Typography variant={isMobile ? 'h5' : 'h4'} sx={{ fontWeight: 900, letterSpacing: '-0.02em' }}>
                    {stats?.win_rate?.toFixed(1) || '0.0'}%
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.92, fontWeight: 700 }}>
                    {stats?.wins || 0} / {stats?.total_bets || 0} apostas
                  </Typography>
                </CardContent>
              </Card>
            </Zoom>
          </Grid>

          {/* Fase */}
          <Grid item xs={6} md={3}>
            <Zoom in timeout={820}>
              <Card
                elevation={0}
                sx={{
                  background: 'linear-gradient(135deg, #FF9800 0%, #FFB74D 100%)',
                  color: 'white',
                  borderRadius: 3,
                  transition: 'all 0.25s ease',
                  '&:hover': { transform: 'translateY(-3px)', boxShadow: '0 10px 24px rgba(255,152,0,0.18)' },
                }}
              >
                <CardContent sx={{ p: { xs: 2, md: 3 } }}>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                    <FlagIcon sx={{ fontSize: isMobile ? 20 : 24 }} />
                    <Typography variant={isMobile ? 'body2' : 'h6'} sx={{ fontWeight: 800 }}>
                      Fase {phase?.phase || 1}
                    </Typography>
                  </Stack>

                  <Typography variant={isMobile ? 'h6' : 'h5'} sx={{ fontWeight: 900, mb: 1 }}>
                    {formatMoney(phase?.target)}
                  </Typography>

                  <LinearProgress
                    variant="determinate"
                    value={phase?.progress || 0}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      bgcolor: 'rgba(255,255,255,0.3)',
                      '& .MuiLinearProgress-bar': { bgcolor: 'white', borderRadius: 4 },
                    }}
                  />

                  <Typography variant="caption" sx={{ opacity: 0.92, mt: 0.6, display: 'block', fontWeight: 800 }}>
                    {phase?.progress?.toFixed(1) || '0.0'}% completo
                  </Typography>
                </CardContent>
              </Card>
            </Zoom>
          </Grid>
        </Grid>

        {/* Insights rápidos */}
        <Fade in timeout={900}>
          <Paper
            elevation={0}
            sx={{
              p: 2,
              borderRadius: 3,
              background: 'white',
              border: '1px solid rgba(0,0,0,0.05)',
              mb: 3,
            }}
          >
            <Stack direction="row" spacing={1.2} alignItems="center" sx={{ mb: 1.5 }}>
              <InsightsIcon sx={{ color: 'primary.main' }} />
              <Typography variant={isMobile ? 'h6' : 'h5'} sx={{ fontWeight: 900 }}>
                Insights rápidos
              </Typography>
            </Stack>

            <Grid container spacing={2}>
              <Grid item xs={6} md={3}>
                <Paper elevation={0} sx={{ p: 1.8, borderRadius: 2.5, border: '1px solid rgba(0,0,0,0.08)' }}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <CasinoIcon color="action" />
                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>
                        Stake total (últimas)
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 900 }}>
                        {formatMoney(derived.totalStake)}
                      </Typography>
                    </Box>
                  </Stack>
                </Paper>
              </Grid>

              <Grid item xs={6} md={3}>
                <Paper elevation={0} sx={{ p: 1.8, borderRadius: 2.5, border: '1px solid rgba(0,0,0,0.08)' }}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <ShowChartIcon color="action" />
                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>
                        Odd média (últimas)
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 900 }}>
                        {derived.avgOdds.toFixed(2)}
                      </Typography>
                    </Box>
                  </Stack>
                </Paper>
              </Grid>

              <Grid item xs={6} md={3}>
                <Paper elevation={0} sx={{ p: 1.8, borderRadius: 2.5, border: '1px solid rgba(0,0,0,0.08)' }}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <PendingActionsIcon color="action" />
                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>
                        Pendentes
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 900 }}>
                        {derived.pendingCount}
                      </Typography>
                    </Box>
                  </Stack>
                </Paper>
              </Grid>

              <Grid item xs={6} md={3}>
                <Paper elevation={0} sx={{ p: 1.8, borderRadius: 2.5, border: '1px solid rgba(0,0,0,0.08)' }}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <EmojiEventsIcon color="action" />
                    <Box>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>
                        Streak (vitórias)
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 900 }}>
                        {derived.streak}
                      </Typography>
                    </Box>
                  </Stack>
                </Paper>
              </Grid>
            </Grid>
          </Paper>
        </Fade>

        {/* Histórico */}
        <Fade in timeout={1000}>
          <Paper
            elevation={0}
            sx={{
              p: { xs: 2, md: 3 },
              borderRadius: 3,
              background: 'white',
              border: '1px solid rgba(0,0,0,0.05)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2, mb: 2 }}>
              <Stack direction="row" spacing={1} alignItems="center">
                <ShowChartIcon sx={{ color: 'primary.main' }} />
                <Typography variant={isMobile ? 'h6' : 'h5'} sx={{ fontWeight: 900 }}>
                  Últimas {isMobile ? '5' : '10'} Apostas
                </Typography>
              </Stack>

              <TextField
                size="small"
                placeholder="Buscar jogo/mercado…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon color="action" />
                    </InputAdornment>
                  ),
                }}
                sx={{ width: isMobile ? '100%' : 280 }}
              />
            </Box>

            {/* filtros rápidos */}
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
              {[
                { key: 'all', label: 'Todas' },
                { key: 'won', label: 'Vitórias' },
                { key: 'lost', label: 'Derrotas' },
                { key: 'pending', label: 'Pendentes' },
                { key: 'void', label: 'Anuladas' },
              ].map((f) => (
                <Chip
                  key={f.key}
                  label={f.label}
                  onClick={() => setStatusFilter(f.key)}
                  variant={statusFilter === f.key ? 'filled' : 'outlined'}
                  color={statusFilter === f.key ? 'primary' : 'default'}
                  sx={{ fontWeight: 800, cursor: 'pointer' }}
                />
              ))}
            </Box>

            <Divider sx={{ mb: 2 }} />

            {/* Mobile: cards / Desktop: tabela */}
            {isMobile ? (
              <Stack spacing={1.5}>
                {filteredHistory.length > 0 ? (
                  filteredHistory.slice(0, 5).map((bet, index) => (
                    <Fade in key={index} timeout={400}>
                      <Paper
                        elevation={0}
                        sx={{
                          p: 1.8,
                          borderRadius: 2.5,
                          border: '1px solid rgba(0,0,0,0.08)',
                        }}
                      >
                        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={1}>
                          <Box sx={{ minWidth: 0 }}>
                            <Typography variant="body2" sx={{ fontWeight: 900 }}>
                              {bet?.match || '-'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>
                              {bet?.market || '-'}
                            </Typography>
                          </Box>
                          {getStatusChip(bet?.status)}
                        </Stack>

                        <Divider sx={{ my: 1.2 }} />

                        <Grid container spacing={1}>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>
                              Odd
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 900 }}>
                              {Number(bet?.odds || 0).toFixed(2)}
                            </Typography>
                          </Grid>

                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>
                              Stake
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 900 }}>
                              {formatMoney(Number(bet?.stake || 0))}
                            </Typography>
                          </Grid>

                          <Grid item xs={12}>
                            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>
                              Data
                            </Typography>
                            <Typography variant="body2" sx={{ fontWeight: 900 }}>
                              {bet?.timestamp
                                ? new Date(bet.timestamp).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
                                : '-'}
                            </Typography>
                          </Grid>

                          {bet?.result !== null && bet?.result !== undefined && (
                            <Grid item xs={12}>
                              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>
                                Resultado
                              </Typography>
                              <Typography
                                variant="body2"
                                sx={{
                                  fontWeight: 900,
                                  color: Number(bet.result) > 0 ? 'success.main' : 'error.main',
                                }}
                              >
                                {formatMoney(Number(bet.result))}
                              </Typography>
                            </Grid>
                          )}
                        </Grid>
                      </Paper>
                    </Fade>
                  ))
                ) : (
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      borderRadius: 3,
                      border: '1px solid rgba(0,0,0,0.08)',
                      textAlign: 'center',
                    }}
                  >
                    <Typography color="text.secondary" variant="body2" sx={{ fontWeight: 800 }}>
                      📭 Nenhuma aposta registrada ainda
                    </Typography>
                  </Paper>
                )}
              </Stack>
            ) : (
              <TableContainer>
                <Table size="medium">
                  <TableHead>
                    <TableRow sx={{ bgcolor: 'grey.50' }}>
                      <TableCell sx={{ fontWeight: 900 }}>Data</TableCell>
                      <TableCell sx={{ fontWeight: 900 }}>Jogo</TableCell>
                      <TableCell sx={{ fontWeight: 900 }}>Mercado</TableCell>
                      {!isTablet && <TableCell align="right" sx={{ fontWeight: 900 }}>Odd</TableCell>}
                      {!isTablet && <TableCell align="right" sx={{ fontWeight: 900 }}>Stake</TableCell>}
                      <TableCell sx={{ fontWeight: 900 }}>Status</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 900 }}>Resultado</TableCell>
                    </TableRow>
                  </TableHead>

                  <TableBody>
                    {filteredHistory.length > 0 ? (
                      filteredHistory.slice(0, 10).map((bet, index) => (
                        <TableRow
                          key={index}
                          hover
                          sx={{
                            '&:hover': { bgcolor: 'grey.50' },
                          }}
                        >
                          <TableCell>
                            {bet?.timestamp
                              ? new Date(bet.timestamp).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
                              : '-'}
                          </TableCell>

                          <TableCell>
                            <Typography variant="body2" sx={{ fontWeight: 800 }}>
                              {bet?.match || '-'}
                            </Typography>
                          </TableCell>

                          <TableCell>{bet?.market || '-'}</TableCell>

                          {!isTablet && <TableCell align="right">{Number(bet?.odds || 0).toFixed(2)}</TableCell>}
                          {!isTablet && <TableCell align="right">{formatMoney(Number(bet?.stake || 0))}</TableCell>}

                          <TableCell>{getStatusChip(bet?.status)}</TableCell>

                          <TableCell align="right">
                            {bet?.result !== null && bet?.result !== undefined ? (
                              <Typography
                                variant="body2"
                                sx={{
                                  color: Number(bet.result) > 0 ? 'success.main' : 'error.main',
                                  fontWeight: 900,
                                }}
                              >
                                {formatMoney(Number(bet.result))}
                              </Typography>
                            ) : (
                              <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 800 }}>
                                -
                              </Typography>
                            )}
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={7} align="center" sx={{ py: 6 }}>
                          <Typography color="text.secondary" variant="body2" sx={{ fontWeight: 800 }}>
                            📭 Nenhuma aposta registrada ainda
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Paper>
        </Fade>

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

export default Dashboard;
