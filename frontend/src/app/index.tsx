"use client";

import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, TouchableOpacity, ScrollView, ActivityIndicator, Switch } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';

// Interface de tipagem para os temas
interface Theme {
  background: string;
  card: string;
  text: string;
  textSecondary: string;
  inputBg: string;
  border: string;
  primary: string;
  primaryHover: string;
  placeholder: string;
  success: string;
}

// Definição das paletas de cores modernas
const lightTheme: Theme = {
  background: '#F9FAFB',
  card: '#FFFFFF',
  text: '#1F2937',
  textSecondary: '#4B5563',
  inputBg: '#F3F4F6',
  border: '#E5E7EB',
  primary: '#3B82F6',
  primaryHover: '#2563EB',
  placeholder: '#9CA3AF',
  success: '#10B981'
};

const darkTheme: Theme = {
  background: '#111827',
  card: '#1F2937',
  text: '#F9FAFB',
  textSecondary: '#D1D5DB',
  inputBg: '#374151',
  border: '#4B5563',
  primary: '#3B82F6',
  primaryHover: '#60A5FA',
  placeholder: '#9CA3AF',
  success: '#34D399'
};

export default function App() {
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);
  const theme: Theme = isDarkMode ? darkTheme : lightTheme;

  const [disciplina, setDisciplina] = useState<string>('');
  const [ementa, setEmenta] = useState<string>('');
  const [horas, setHoras] = useState<string>('');
  const [arquivoPdf, setArquivoPdf] = useState<DocumentPicker.DocumentPickerAsset | null>(null);
  const [roteiro, setRoteiro] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const toggleTheme = () => setIsDarkMode(previousState => !previousState);

  const selecionarArquivo = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'application/pdf',
        copyToCacheDirectory: true,
      });
      
      if (!result.canceled && result.assets && result.assets.length > 0) {
        setArquivoPdf(result.assets[0]);
        setEmenta(''); 
      }
    } catch (err) {
      console.log("Erro ao selecionar o arquivo:", err);
    }
  };

  const gerarRoteiro = async () => {
    if (!disciplina || !horas || (!ementa && !arquivoPdf)) {
      setRoteiro('Por favor, preencha os campos obrigatórios e forneça a ementa (via texto ou PDF).');
      return;
    }

    setLoading(true);
    setRoteiro('');
    
    const formData = new FormData();
    formData.append('disciplina', disciplina);
    formData.append('horas_semanais', horas);
    
    if (arquivoPdf) {
      formData.append('arquivo', {
        uri: arquivoPdf.uri,
        name: arquivoPdf.name,
        type: arquivoPdf.mimeType || 'application/pdf'
      } as any);
    } else {
      formData.append('ementa', ementa);
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/gerar-roteiro', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      if (response.ok) {
        setRoteiro(data.roteiro);
      } else {
        setRoteiro(`Erro: ${data.detail}`);
      }
    } catch (error) {
      setRoteiro("Erro de conexão. Certifique-se de que a API local está rodando.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={[styles.container, { backgroundColor: theme.background }]}>
      <View style={[styles.card, { backgroundColor: theme.card, borderColor: theme.border }]}>
        
        <View style={styles.header}>
          <Text style={[styles.title, { color: theme.text }]}>EstudaAI</Text>
          <View style={styles.themeToggle}>
            <Text style={{ color: theme.text, fontSize: 14, marginRight: 8, fontWeight: 'bold' }}>
              Tema Escuro
            </Text>
            <Switch
              trackColor={{ false: "#D1D5DB", true: "#93C5FD" }}
              thumbColor={isDarkMode ? theme.primary : "#FFFFFF"}
              onValueChange={toggleTheme}
              value={isDarkMode}
            />
          </View>
        </View>

        <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
          Planeje sua semana de estudos. Cole a ementa ou envie o arquivo PDF.
        </Text>
        
        <TextInput 
          style={[styles.input, { backgroundColor: theme.inputBg, color: theme.text, borderColor: theme.border }]} 
          placeholderTextColor={theme.placeholder}
          placeholder="Qual a disciplina? (ex: Cálculo I)" 
          value={disciplina} 
          onChangeText={setDisciplina} 
        />
        
        <TextInput 
          style={[styles.input, { backgroundColor: theme.inputBg, color: theme.text, borderColor: theme.border }]} 
          placeholderTextColor={theme.placeholder}
          placeholder="Horas disponíveis por semana? (ex: 10)" 
          value={horas} 
          onChangeText={setHoras} 
          keyboardType="numeric" 
        />

        <Text style={{ color: theme.text, marginBottom: 10, fontWeight: 'bold' }}>Opção 1: Digite ou cole a ementa</Text>
        <TextInput 
          style={[styles.input, styles.textArea, { backgroundColor: theme.inputBg, color: theme.text, borderColor: theme.border }]} 
          placeholderTextColor={theme.placeholder}
          placeholder="Cole a ementa ou os tópicos da matéria aqui..." 
          value={ementa} 
          onChangeText={(texto) => {
            setEmenta(texto);
            if (texto.length > 0) setArquivoPdf(null);
          }} 
          multiline 
        />

        <Text style={{ color: theme.text, marginBottom: 10, marginTop: 10, fontWeight: 'bold', textAlign: 'center' }}>OU</Text>

        <TouchableOpacity 
          style={[styles.fileButton, { borderColor: theme.primary }]} 
          onPress={selecionarArquivo}
        >
          <Text style={[styles.fileButtonText, { color: arquivoPdf ? theme.success : theme.primary }]}>
            {arquivoPdf ? `Arquivo selecionado: ${arquivoPdf.name}` : "Opção 2: Enviar arquivo PDF"}
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.button, { backgroundColor: theme.primary }]} 
          onPress={gerarRoteiro} 
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Montar meu roteiro</Text>
          )}
        </TouchableOpacity>
      </View>

      {roteiro ? (
        <View style={[styles.resultContainer, { backgroundColor: theme.card, borderColor: theme.border }]}>
          <Text style={[styles.resultTitle, { color: theme.text }]}>Seu Roteiro de Estudos:</Text>
          <Text style={[styles.resultText, { color: theme.textSecondary }]}>{roteiro}</Text>
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { 
    padding: 20, 
    flexGrow: 1, 
    alignItems: 'center',
    justifyContent: 'flex-start',
  },
  card: {
    width: '100%',
    maxWidth: 600,
    padding: 30,
    borderRadius: 16,
    borderWidth: 1,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 3,
    marginTop: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  title: { 
    fontSize: 28, 
    fontWeight: '800', 
    letterSpacing: -0.5,
  },
  themeToggle: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  subtitle: {
    fontSize: 16,
    marginBottom: 25,
    lineHeight: 24,
  },
  input: { 
    padding: 16, 
    borderRadius: 12, 
    marginBottom: 16, 
    borderWidth: 1, 
    fontSize: 16,
  },
  textArea: { 
    height: 100, 
    textAlignVertical: 'top' 
  },
  fileButton: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderStyle: 'dashed',
    alignItems: 'center',
    marginBottom: 20,
  },
  fileButtonText: {
    fontWeight: '700',
    fontSize: 16,
  },
  button: { 
    padding: 18, 
    borderRadius: 12, 
    alignItems: 'center',
    marginTop: 10,
    shadowColor: "#3B82F6",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  buttonText: { 
    color: '#fff', 
    fontWeight: '700', 
    fontSize: 18,
    letterSpacing: 0.5,
  },
  resultContainer: { 
    width: '100%',
    maxWidth: 600,
    marginTop: 24, 
    padding: 30, 
    borderRadius: 16, 
    borderWidth: 1, 
  },
  resultTitle: { 
    fontSize: 20, 
    fontWeight: '700', 
    marginBottom: 15,
  },
  resultText: { 
    fontSize: 16, 
    lineHeight: 28,
  }
});