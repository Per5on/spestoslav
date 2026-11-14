import React, { useEffect, useState } from 'react';
import { ActivityIndicator, FlatList, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

export type Locality = { id: string; name: string; name_bg?: string | null; postal_code?: string | null; type: string; municipality?: string | null; region?: string | null };
type Props = { apiBaseUrl: string; selected: Locality | null; onSelect: (value: Locality) => void };

export function LocationPicker({ apiBaseUrl, selected, onSelect }: Props) {
  const [query, setQuery] = useState(selected?.name_bg || selected?.name || '');
  const [results, setResults] = useState<Locality[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    const term = query.trim();
    if (term.length < 2) { setResults([]); setLoading(false); return; }
    let cancelled = false;
    const timer = setTimeout(async () => {
      setLoading(true); setError('');
      try {
        const response = await fetch(apiBaseUrl.replace(/\\/$/, '') + '/api/v1/localities?q=' + encodeURIComponent(term));
        if (!response.ok) throw new Error('Search unavailable');
        const data: Locality[] = await response.json();
        if (!cancelled) setResults(data);
      } catch { if (!cancelled) setError('Неуспешно зареждане. Опитайте отново.'); }
      finally { if (!cancelled) setLoading(false); }
    }, 250);
    return () => { cancelled = true; clearTimeout(timer); };
  }, [query, apiBaseUrl]);
  return <View style={styles.wrap}>
    <Text style={styles.label}>Населено място</Text>
    <TextInput value={query} onChangeText={(v) => { setQuery(v); setOpen(true); }} onFocus={() => setOpen(true)} placeholder="Търси град, село или пощенски код" autoCorrect={false} style={styles.input} accessibilityLabel="Търсене на населено място или пощенски код" />
    {open && query.trim().length >= 2 && <View style={styles.menu}>
      {loading ? <ActivityIndicator /> : error ? <Text style={styles.empty}>{error}</Text> : <FlatList keyboardShouldPersistTaps="handled" data={results} keyExtractor={(x) => x.id} ListEmptyComponent={<Text style={styles.empty}>Няма намерени населени места</Text>} renderItem={({item}) => <Pressable style={styles.option} onPress={() => { onSelect(item); setQuery(item.name_bg || item.name); setOpen(false); }}><Text style={styles.optionTitle}>{item.name_bg || item.name}</Text><Text style={styles.meta}>{[item.postal_code, item.municipality, item.region].filter(Boolean).join(' · ')}</Text></Pressable>} />}
    </View>}
    {selected && <Text style={styles.selected}>Избрано: {selected.name_bg || selected.name}</Text>}
  </View>;
}
const styles = StyleSheet.create({wrap:{gap:6,zIndex:10},label:{color:'#294E31',fontWeight:'700'},input:{backgroundColor:'#FFF',borderColor:'#D9E5D9',borderWidth:1,borderRadius:12,padding:13,color:'#203D28'},menu:{maxHeight:260,backgroundColor:'#FFF',borderWidth:1,borderColor:'#D9E5D9',borderRadius:12,overflow:'hidden'},option:{padding:12,borderBottomWidth:StyleSheet.hairlineWidth,borderBottomColor:'#E5ECE4'},optionTitle:{color:'#203D28',fontWeight:'700'},meta:{color:'#758276',fontSize:12,marginTop:3},empty:{color:'#758276',padding:14},selected:{color:'#52775A',fontSize:12}});
