import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  Box,
  Container,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  useTheme,
  useMediaQuery,
  Fade,
  Chip,
  Stack,
  Tooltip,
  Collapse,
  Snackbar,
  Button,
  Grow,
  LinearProgress,
} from '@mui/material';

import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import RefreshIcon from '@mui/icons-material/Refresh';
import WifiIcon from '@mui/icons-material/Wifi';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import ThumbUpAltOutlinedIcon from '@mui/icons-material/ThumbUpAltOutlined';
import ThumbDownAltOutlinedIcon from '@mui/icons-material/ThumbDownAltOutlined';
import SportsIcon from '@mui/icons-material/Sports';
import SportsFootballIcon from '@mui/icons-material/SportsFootball';
import SportsTennisIcon from '@mui/icons-material/SportsTennis';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';

import { sendChatMessage } from '../services/api';

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Olá! 👋 Sou seu assistente de value betting. Como posso ajudar você hoje?',
    },
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const [errorMsg, setErrorMsg] = useState('');
  const [snack, setSnack] = useState({ open: false, message: '' });

  const [showScrollDown, setShowScrollDown] = useState(false);

  const messagesEndRef = useRef(null);
  const scrollAreaRef = useRef(null);
  const lastUserInputRef = useRef('');

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const quickQuestions = useMemo(
    () => [
      { 
        icon: <TrendingUpIcon fontSize="small" />, 
        label: '💡 O que é EV?', 
        prompt: 'O que é EV e como interpretar?',
        color: '#00A859' 
      },
      { 
        icon: <SportsIcon fontSize="small" />, 
        label: '⚽ Jogos de futebol hoje?', 
        prompt: 'Quais os jogos de futebol hoje e onde há oportunidades?',
        color: '#00A859'
      },
      { 
        icon: <SportsFootballIcon fontSize="small" />, 
        label: '🏈 Jogos de NFL hoje?', 
        prompt: 'Quais são os jogos de NFL disponíveis hoje?',
        color: '#ED6C02'
      },
      { 
        icon: <SportsTennisIcon fontSize="small" />, 
        label: '🎾 Partidas de tênis ao vivo?', 
        prompt: 'Quais partidas de tênis estão acontecendo agora?',
        color: '#9C27B0'
      },
      { 
        icon: <AttachMoneyIcon fontSize="small" />, 
        label: '💰 Gestão de banca', 
        prompt: 'Como funciona a gestão de banca e stake sugerido?',
        color: '#00A859'
      },
      { 
        icon: <TrendingUpIcon fontSize="small" />, 
        label: '📈 Múltiplas valem a pena?', 
        prompt: 'Vale a pena fazer múltiplas? Quando faz sentido?',
        color: '#00A859'
      },
    ],
    []
  );

  const formatTime = () =>
    new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

  const status = useMemo(() => {
    if (errorMsg) return { label: 'Problema de conexão', icon: <ErrorOutlineIcon fontSize="small" />, color: 'error' };
    if (loading) return { label: 'Digitando…', icon: <AutoAwesomeIcon fontSize="small" />, color: 'primary' };
    return { label: 'Online', icon: <WifiIcon fontSize="small" />, color: 'success' };
  }, [loading, errorMsg]);

  const scrollToBottom = useCallback((behavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  }, []);

  const handleScroll = useCallback(() => {
    const el = scrollAreaRef.current;
    if (!el) return;

    const distanceFromBottom = el.scrollHeight - (el.scrollTop + el.clientHeight);
    setShowScrollDown(distanceFromBottom > 220);
  }, []);

  useEffect(() => {
    if (!showScrollDown) scrollToBottom('smooth');
  }, [messages, loading, showScrollDown, scrollToBottom]);

  useEffect(() => {
    const el = scrollAreaRef.current;
    if (!el) return;

    handleScroll();
    el.addEventListener('scroll', handleScroll);
    return () => el.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  const safeCopy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setSnack({ open: true, message: 'Copiado ✅' });
    } catch {
      setSnack({ open: true, message: 'Não consegui copiar automaticamente.' });
    }
  };

  const addMessage = (msg) => setMessages((prev) => [...prev, msg]);

  const send = async (text) => {
    const content = (text ?? input).trim();
    if (!content || loading) return;

    setErrorMsg('');
    lastUserInputRef.current = content;

    const userMessage = { role: 'user', content };
    addMessage(userMessage);

    setInput('');
    setLoading(true);

    try {
      const response = await sendChatMessage(content);
      const assistantMessage = { role: 'assistant', content: response?.message || 'Sem resposta no momento.' };
      addMessage(assistantMessage);
    } catch (error) {
      console.error('Erro no chat:', error);
      setErrorMsg('Falha ao enviar. Tente novamente.');
      addMessage({
        role: 'assistant',
        content: 'Desculpe, ocorreu um erro ao enviar. 😔 Você pode tentar novamente.',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSend = () => send(input);

  const handleRetry = () => {
    if (!lastUserInputRef.current) return;
    send(lastUserInputRef.current);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    setMessages([
      { role: 'assistant', content: 'Chat limpo ✅ Como posso te ajudar agora?' },
    ]);
    setErrorMsg('');
    setSnack({ open: true, message: 'Chat limpo.' });
    setTimeout(() => scrollToBottom('auto'), 50);
  };

  const isFirstScreen = messages.length === 1;

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #F5F7FA 0%, #E8EEF2 100%)',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Container
        maxWidth="md"
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          py: { xs: 2, md: 3 },
        }}
      >
        <Fade in timeout={600}>
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AutoAwesomeIcon sx={{ color: 'primary.main', fontSize: isMobile ? 28 : 32 }} />
                <Box>
                  <Typography
                    variant={isMobile ? 'h5' : 'h4'}
                    sx={{
                      fontWeight: 900,
                      background: 'linear-gradient(135deg, #00A859 0%, #00763E 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      lineHeight: 1.05,
                    }}
                  >
                    Chat com Agente
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.4 }}>
                    Tire suas dúvidas sobre value betting • {formatTime()}
                  </Typography>
                </Box>
              </Box>

              <Stack direction="row" spacing={1} alignItems="center">
                <Chip
                  icon={status.icon}
                  label={status.label}
                  color={status.color}
                  variant={status.color === 'success' ? 'outlined' : 'filled'}
                  sx={{ fontWeight: 800 }}
                />

                <Tooltip title="Limpar chat">
                  <IconButton
                    onClick={handleClear}
                    sx={{
                      border: '1px solid rgba(0,0,0,0.08)',
                      borderRadius: 2,
                      bgcolor: 'white',
                    }}
                  >
                    <DeleteOutlineIcon />
                  </IconButton>
                </Tooltip>

                <Tooltip title="Ir para o final">
                  <IconButton
                    onClick={() => scrollToBottom('smooth')}
                    sx={{
                      border: '1px solid rgba(0,0,0,0.08)',
                      borderRadius: 2,
                      bgcolor: 'white',
                    }}
                  >
                    <ArrowDownwardIcon />
                  </IconButton>
                </Tooltip>
              </Stack>
            </Box>

            <Collapse in={!loading && isFirstScreen}>
              <Paper
                elevation={0}
                sx={{
                  mt: 2,
                  p: 1.5,
                  borderRadius: 3,
                  border: '1px solid rgba(0,0,0,0.08)',
                  bgcolor: 'rgba(0,0,0,0.02)',
                }}
              >
                <Typography variant="body2" sx={{ fontWeight: 700 }}>
                  Dica: pressione <b>Enter</b> para enviar e <b>Shift + Enter</b> para quebrar linha.
                </Typography>
              </Paper>
            </Collapse>
          </Box>
        </Fade>

        {isFirstScreen && (
          <Fade in timeout={800}>
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block', fontWeight: 800 }}>
                Sugestões rápidas:
              </Typography>

              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {quickQuestions.map((q, index) => (
                  <Chip
                    key={index}
                    icon={q.icon}
                    label={q.label}
                    onClick={() => send(q.prompt)}
                    sx={{
                      cursor: 'pointer',
                      fontWeight: 700,
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        bgcolor: q.color,
                        color: 'white',
                        transform: 'translateY(-2px)',
                        boxShadow: 2,
                        '& .MuiChip-icon': {
                          color: 'white',
                        },
                      },
                    }}
                  />
                ))}
              </Box>
            </Box>
          </Fade>
        )}

        <Paper
          elevation={0}
          sx={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            borderRadius: 3,
            border: '1px solid rgba(0,0,0,0.05)',
            background: 'white',
            position: 'relative',
          }}
        >
          <Collapse in={loading}>
            <LinearProgress />
          </Collapse>

          <Box
            ref={scrollAreaRef}
            sx={{
              flex: 1,
              overflowY: 'auto',
              p: { xs: 2, md: 3 },
              background: 'linear-gradient(180deg, #FAFBFC 0%, #FFFFFF 100%)',
              '&::-webkit-scrollbar': { width: '8px' },
              '&::-webkit-scrollbar-track': { background: 'transparent' },
              '&::-webkit-scrollbar-thumb': { background: '#D1D5DB', borderRadius: '4px' },
            }}
          >
            <Stack alignItems="center" sx={{ mb: 2 }}>
              <Chip
                label="Hoje"
                size="small"
                sx={{
                  bgcolor: 'rgba(0,0,0,0.06)',
                  fontWeight: 800,
                }}
              />
            </Stack>

            {messages.map((msg, index) => {
              const isUser = msg.role === 'user';
              const isAssistant = msg.role === 'assistant';

              return (
                <Grow in key={index} timeout={260}>
                  <Box
                    sx={{
                      display: 'flex',
                      mb: 2.5,
                      justifyContent: isUser ? 'flex-end' : 'flex-start',
                      gap: 1.5,
                    }}
                  >
                    {isAssistant && (
                      <Avatar
                        sx={{
                          bgcolor: 'primary.main',
                          width: isMobile ? 36 : 40,
                          height: isMobile ? 36 : 40,
                          boxShadow: '0 4px 12px rgba(0,168,89,0.3)',
                        }}
                      >
                        <SmartToyIcon fontSize="small" />
                      </Avatar>
                    )}

                    <Box sx={{ maxWidth: { xs: '82%', md: '72%' } }}>
                      <Paper
                        elevation={0}
                        sx={{
                          p: { xs: 1.5, md: 2 },
                          background: isUser
                            ? 'linear-gradient(135deg, #00A859 0%, #00C46A 100%)'
                            : 'white',
                          color: isUser ? 'white' : 'text.primary',
                          borderRadius: 3,
                          border: isAssistant ? '1px solid rgba(0,0,0,0.08)' : 'none',
                          boxShadow: isUser
                            ? '0 4px 12px rgba(0,168,89,0.3)'
                            : '0 2px 8px rgba(0,0,0,0.08)',
                          position: 'relative',
                        }}
                      >
                        {isAssistant ? (
                          <ReactMarkdown
                            components={{
                              p: ({node, ...props}) => <Typography variant="body1" sx={{ mb: 1, lineHeight: 1.65 }} {...props} />,
                              h3: ({node, ...props}) => <Typography variant="h6" sx={{ fontWeight: 700, mt: 1.5, mb: 1 }} {...props} />,
                              li: ({node, ...props}) => <li style={{ marginLeft: '1.2rem', marginBottom: '0.4rem' }} {...props} />,
                              code: ({node, inline, ...props}) => (
                                <code style={{
                                  backgroundColor: 'rgba(0,0,0,0.06)',
                                  padding: inline ? '2px 6px' : '12px',
                                  borderRadius: '4px',
                                  display: inline ? 'inline' : 'block',
                                  fontSize: '0.9em',
                                  fontFamily: 'monospace'
                                }} {...props} />
                              ),
                            }}
                          >
                            {msg.content}
                          </ReactMarkdown>
                        ) : (
                          <Typography
                            variant="body1"
                            sx={{
                              whiteSpace: 'pre-wrap',
                              lineHeight: 1.65,
                              fontSize: isMobile ? '0.92rem' : '1rem',
                            }}
                          >
                            {msg.content}
                          </Typography>
                        )}

                        {isAssistant && (
                          <Box
                            sx={{
                              mt: 1.3,
                              pt: 1,
                              borderTop: '1px solid rgba(0,0,0,0.06)',
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              gap: 1,
                            }}
                          >
                            <Stack direction="row" spacing={0.5} alignItems="center">
                              <Tooltip title="Copiar">
                                <IconButton size="small" onClick={() => safeCopy(msg.content)}>
                                  <ContentCopyIcon fontSize="inherit" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Gostei">
                                <IconButton
                                  size="small"
                                  onClick={() => setSnack({ open: true, message: 'Feedback enviado 👍' })}
                                >
                                  <ThumbUpAltOutlinedIcon fontSize="inherit" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Não gostei">
                                <IconButton
                                  size="small"
                                  onClick={() => setSnack({ open: true, message: 'Feedback enviado 👎' })}
                                >
                                  <ThumbDownAltOutlinedIcon fontSize="inherit" />
                                </IconButton>
                              </Tooltip>
                            </Stack>

                            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 700 }}>
                              {formatTime()}
                            </Typography>
                          </Box>
                        )}
                      </Paper>
                    </Box>

                    {isUser && (
                      <Avatar
                        sx={{
                          bgcolor: 'secondary.main',
                          width: isMobile ? 36 : 40,
                          height: isMobile ? 36 : 40,
                          boxShadow: '0 4px 12px rgba(33,33,33,0.3)',
                        }}
                      >
                        <PersonIcon fontSize="small" />
                      </Avatar>
                    )}
                  </Box>
                </Grow>
              );
            })}

            {loading && (
              <Fade in>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2.5, gap: 1.5 }}>
                  <Avatar
                    sx={{
                      bgcolor: 'primary.main',
                      width: isMobile ? 36 : 40,
                      height: isMobile ? 36 : 40,
                    }}
                  >
                    <SmartToyIcon fontSize="small" />
                  </Avatar>

                  <Paper
                    elevation={0}
                    sx={{
                      p: 2,
                      borderRadius: 3,
                      border: '1px solid rgba(0,0,0,0.08)',
                      bgcolor: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1.5,
                    }}
                  >
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      {[0, 0.2, 0.4].map((delay, i) => (
                        <Box
                          key={i}
                          sx={{
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            bgcolor: 'primary.main',
                            animation: 'pulse 1.4s infinite',
                            animationDelay: `${delay}s`,
                            '@keyframes pulse': {
                              '0%, 80%, 100%': { opacity: 0.35 },
                              '40%': { opacity: 1 },
                            },
                          }}
                        />
                      ))}
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 700 }}>
                      Digitando…
                    </Typography>
                  </Paper>
                </Box>
              </Fade>
            )}

            <div ref={messagesEndRef} />
          </Box>

          <Fade in={showScrollDown}>
            <Box
              sx={{
                position: 'absolute',
                right: 16,
                bottom: 92,
                zIndex: 5,
              }}
            >
              <Tooltip title="Descer para a última mensagem">
                <IconButton
                  onClick={() => scrollToBottom('smooth')}
                  sx={{
                    bgcolor: 'white',
                    border: '1px solid rgba(0,0,0,0.08)',
                    boxShadow: '0 10px 24px rgba(0,0,0,0.12)',
                    '&:hover': { bgcolor: 'grey.50' },
                  }}
                >
                  <ArrowDownwardIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Fade>

          <Box
            sx={{
              p: { xs: 2, md: 2.5 },
              bgcolor: 'white',
              borderTop: '1px solid rgba(0,0,0,0.08)',
            }}
          >
            <Collapse in={!!errorMsg}>
              <Paper
                elevation={0}
                sx={{
                  mb: 1.5,
                  p: 1.2,
                  borderRadius: 2.5,
                  border: '1px solid rgba(0,0,0,0.08)',
                  bgcolor: 'rgba(255,0,0,0.04)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 1,
                }}
              >
                <Stack direction="row" spacing={1} alignItems="center">
                  <ErrorOutlineIcon color="error" fontSize="small" />
                  <Typography variant="body2" sx={{ fontWeight: 800 }}>
                    {errorMsg}
                  </Typography>
                </Stack>

                <Button
                  size="small"
                  variant="contained"
                  onClick={handleRetry}
                  startIcon={<RefreshIcon />}
                  sx={{ fontWeight: 900, borderRadius: 2 }}
                >
                  Reenviar
                </Button>
              </Paper>
            </Collapse>

            <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
              <TextField
                fullWidth
                variant="outlined"
                placeholder="Digite sua mensagem…"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading}
                multiline
                maxRows={5}
                helperText="Enter envia • Shift+Enter quebra linha"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 3,
                    bgcolor: 'grey.50',
                    '&:hover': { bgcolor: 'grey.100' },
                    '&.Mui-focused': { bgcolor: 'white' },
                  },
                  '& .MuiFormHelperText-root': {
                    marginLeft: 0.5,
                    fontWeight: 700,
                  },
                }}
              />

              <IconButton
                onClick={handleSend}
                disabled={!input.trim() || loading}
                sx={{
                  width: { xs: 48, md: 56 },
                  height: { xs: 48, md: 56 },
                  background: 'linear-gradient(135deg, #00A859 0%, #00C46A 100%)',
                  color: 'white',
                  boxShadow: '0 4px 12px rgba(0,168,89,0.3)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #00763E 0%, #00A859 100%)',
                    transform: 'scale(1.05)',
                  },
                  '&:disabled': {
                    bgcolor: 'grey.300',
                    color: 'grey.500',
                  },
                  transition: 'all 0.2s ease',
                  borderRadius: 3,
                }}
              >
                <SendIcon />
              </IconButton>
            </Box>
          </Box>
        </Paper>

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

export default Chat;