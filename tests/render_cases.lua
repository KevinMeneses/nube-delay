-- Carga Nube Delay en una pestaña nueva, renderiza cada caso y cierra la pestaña.
-- Uso: REAPER -nonewinst tests/render_cases.lua   (escribe tests/out/*.wav y tests/out/log.txt)
local ROOT = os.getenv("HOME") .. "/Music/NubeDelay/tests"
local OUT = ROOT .. "/out"
local FX = "JS:Nube Delay/nube_delay.jsfx"
local PRESET = 21
os.execute('mkdir -p "' .. OUT .. '"')
local logf = io.open(OUT .. "/log.txt", "w")
local function log(...) local t = {} for _, v in ipairs({...}) do t[#t+1] = tostring(v) end logf:write(table.concat(t, " "), "\n") logf:flush() end

-- slider N (1..21) = parámetro N-1. Los sliders con forma :log=mid van normalizados 0..1
local LOGP = {[1] = {1, 2000, 300}, [8] = {20, 2000, 200}, [9] = {1000, 20000, 5000}, [12] = {0.05, 5, 0.6}, [17] = {50, 2000, 300}}
local function to_norm(s, v)
  local mn, mx, mid = table.unpack(LOGP[s])
  local sr = (mx - mn) / (mid - mn) - 1; local r = sr * sr
  return math.log((v - mn) / (mx - mn) * (r - 1) + 1) / math.log(r)
end
local function with(a, b) local r = {} for k, v in pairs(a) do r[k] = v end for k, v in pairs(b or {}) do r[k] = v end return r end
-- base: Digital, 250 ms, feedback 50, envío (solo eco), sin filtros ni color
local B = {[1] = 250, [2] = 0, [3] = 0, [4] = 50, [5] = 25, [6] = 0, [7] = 0, [8] = 20, [9] = 20000, [10] = 0, [11] = 0,
           [13] = 0, [14] = 100, [15] = 0, [18] = 0, [19] = 1, [20] = 0}

local CASES = {
  {"echo",      "impulse.wav",  B},
  {"sync_q",    "impulse.wav",  with(B, {[2] = 9})},
  {"sync_dot8", "impulse.wav",  with(B, {[2] = 8})},
  {"pingpong",  "impulseL.wav", with(B, {[6] = 1})},
  {"desfase",   "impulse.wav",  with(B, {[3] = 20})},
  {"mono",      "impulseL.wav", with(B, {[6] = 2})},
  {"fb0",       "impulse.wav",  with(B, {[4] = 0})},
  {"fb100",     "impulse.wav",  with(B, {[4] = 100, [1] = 200})},
  {"mix0",      "impulse.wav",  with(B, {[19] = 0, [5] = 0})},
  {"mix50",     "impulse.wav",  with(B, {[19] = 0, [5] = 50})},
  {"hp400",     "s100.wav",     with(B, {[4] = 0, [8] = 400})},
  {"lp2k",      "s8k.wav",      with(B, {[4] = 0, [9] = 2000})},
  {"duck",      "duck.wav",     with(B, {[1] = 300, [4] = 60, [15] = 12, [16] = -40})},
  {"noduck",    "duck.wav",     with(B, {[1] = 300, [4] = 60})},
  {"width0",    "lr.wav",       with(B, {[4] = 0, [14] = 0})},
  {"sat0",      "s1k_m6.wav",   with(B, {[4] = 0})},
  {"sat100",    "s1k_m6.wav",   with(B, {[4] = 0, [10] = 100})},
  {"mod100",    "s1k_m6.wav",   with(B, {[4] = 0, [11] = 100, [12] = 1})},
  {"dif100",    "impulse.wav",  with(B, {[4] = 0, [13] = 100})},
  {"freeze",    "impulse.wav",  with(B, {[18] = 1})},
  {"salida",    "impulse.wav",  with(B, {[20] = -6})},
}
for st = 0, 4 do CASES[#CASES + 1] = {"style" .. st, "impulse.wav", with(B, {[7] = st})} end
for p = 1, 11 do CASES[#CASES + 1] = {"preset" .. p, "voz.wav", {[PRESET] = p}} end
CASES[#CASES + 1] = {"voz_seca", "voz.wav", {[PRESET] = 11, [5] = 0}}

reaper.Main_OnCommand(40859, 0) -- nueva pestaña
reaper.GetSetProjectInfo(0, "PROJECT_SRATE", 48000, true)
reaper.GetSetProjectInfo(0, "PROJECT_SRATE_USE", 1, true)
reaper.SetCurrentBPM(0, 120, false)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local item = reaper.AddMediaItemToTrack(tr)
local take = reaper.AddTakeToMediaItem(item)
reaper.SetMediaItemInfo_Value(item, "D_POSITION", 0)
local only = os.getenv("NUBE_CASE")

for _, c in ipairs(CASES) do
  local name, src, params = c[1], c[2], c[3]
  if not only or name:find(only) then
    reaper.SetMediaTrackInfo_Value(tr, "I_NCHAN", c[4] or 2)
    local s = reaper.PCM_Source_CreateFromFile(ROOT .. "/signals/" .. src)
    reaper.SetMediaItemTake_Source(take, s)
    reaper.SetMediaItemTakeInfo_Value(take, "D_VOL", 10 ^ ((c[5] or 0) / 20))
    reaper.SetMediaItemInfo_Value(item, "D_LENGTH", math.min(reaper.GetMediaSourceLength(s), 30))
    reaper.SetMediaItemInfo_Value(item, "D_FADEINLEN", 0); reaper.SetMediaItemInfo_Value(item, "D_FADEOUTLEN", 0)
    reaper.UpdateItemInProject(item)
    while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
    local fx = reaper.TrackFX_AddByName(tr, FX, false, -1)
    if fx < 0 then log("ERROR no cargó el FX") break end
    if params[PRESET] then reaper.TrackFX_SetParam(tr, fx, PRESET - 1, params[PRESET]) end
    for s_, v in pairs(params) do
      if s_ ~= PRESET then
        if LOGP[s_] then reaper.TrackFX_SetParamNormalized(tr, fx, s_ - 1, to_norm(s_, v))
        else reaper.TrackFX_SetParam(tr, fx, s_ - 1, v) end
      end
    end
    local file = OUT .. "/" .. name .. ".wav"
    os.remove(file)
    reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true)
    reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
    reaper.GetSetProjectInfo(0, "RENDER_SRATE", 48000, true)
    reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
    reaper.GetSetProjectInfo(0, "RENDER_TAILFLAG", 0, true)
    reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true)
    reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", name, true)
    reaper.Main_OnCommand(42230, 0)
    local vals = {}
    for k = 1, 20 do local _, v = reaper.TrackFX_GetFormattedParamValue(tr, fx, k - 1, ""); vals[#vals + 1] = v end
    log("caso", name, table.concat(vals, " | "))
  end
end
reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_test.rpp", 0)
reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_test.rpp")
reaper.Main_OnCommand(40860, 0) -- cerrar pestaña
log("done")
logf:close()
