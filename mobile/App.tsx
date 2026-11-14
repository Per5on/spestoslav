import React, { useState } from 'react';
import {
  Pressable,
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { LocationPicker, Locality } from './src/location/LocationPicker';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:8000';

const tabs = [
  { id: 'food', bg: 'Храни', en: 'Food', icon: '🛒' },
  { id: 'fuel', bg: 'Горива', en: 'Fuel', icon: '⛽' },
  { id: 'home', bg: 'Дом', en: 'Home', icon: '🏠' },
  { id: 'technology', bg: 'Техника', en: 'Technology', icon: '💻' },
];

export default function App() {
  const [active, setActive] = useState('food');
  // One app-level selection is shared by all four category tabs.
  const [selectedLocality, setSelectedLocality] = useState<Locality | null>(null);
  const language = 'bg';
  const tab = tabs.find((item) => item.id === active) ?? tabs[0];

  return (
    <SafeAreaView style={styles.page}>
      <StatusBar barStyle="light-content" />
      <View style={styles.header}>
        <Text style={styles.brand}>🐷 Спестослав</Text>
        <Text style={styles.tagline}>Сравнявай. Избирай. Спестявай.</Text>
      </View>

      <View style={styles.tabs}>
        {tabs.map((item) => (
          <Pressable
            accessibilityRole="tab"
            accessibilityState={{ selected: active === item.id }}
            key={item.id}
            onPress={() => setActive(item.id)}
            style={[styles.tab, active === item.id && styles.selected]}
          >
            <Text style={styles.icon}>{item.icon}</Text>
            <Text style={[styles.tabText, active === item.id && styles.selectedText]}>
              {language === 'bg' ? item.bg : item.en}
            </Text>
          </Pressable>
        ))}
      </View>

      <View style={styles.body}>
        <Text style={styles.heading}>{tab.bg}</Text>
        <LocationPicker
          apiBaseUrl={API_BASE_URL}
          selected={selectedLocality}
          onSelect={setSelectedLocality}
        />
        <View style={styles.card}>
          <Text style={styles.pig}>🐷</Text>
          <Text style={styles.cardTitle}>Добре дошли в Спестослав</Text>
          <Text style={styles.copy}>
            Изберете населено място, за да сравнявате наличните предложения.
          </Text>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: '#F7FAF5' },
  header: { backgroundColor: '#276B3A', padding: 20, paddingTop: 24 },
  brand: { fontSize: 28, fontWeight: '800', color: '#FFF' },
  tagline: { color: '#E5F2E6', marginTop: 5 },
  tabs: { flexDirection: 'row', backgroundColor: '#FFF', padding: 8, gap: 5 },
  tab: { flex: 1, alignItems: 'center', paddingVertical: 10, borderRadius: 12 },
  selected: { backgroundColor: '#F28C28' },
  icon: { fontSize: 20 },
  tabText: { fontSize: 12, fontWeight: '700', color: '#35533B' },
  selectedText: { color: '#FFF' },
  body: { padding: 18, gap: 16 },
  heading: { fontSize: 24, fontWeight: '800', color: '#234E2D' },
  card: {
    padding: 24,
    backgroundColor: '#FFF',
    borderRadius: 18,
    alignItems: 'center',
    gap: 10,
    borderWidth: 1,
    borderColor: '#E2EAE0',
  },
  pig: { fontSize: 46 },
  cardTitle: { fontSize: 18, fontWeight: '700', color: '#294E31' },
  copy: { textAlign: 'center', color: '#718174', lineHeight: 21 },
});
